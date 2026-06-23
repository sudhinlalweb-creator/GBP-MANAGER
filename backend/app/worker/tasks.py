"""Background tasks for SERP acquisition workflows."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.email import send_billing_alert, send_org_invite, send_password_reset
from app.db.session import AsyncSessionLocal
from app.models.keyword import Keyword
from app.models.ranking_history import RankingHistory
from app.organizations.models import Organization, OrganizationMembership
from app.models.user import User
from app.services.serp.client import HTTPGoogleSERPClient
from app.services.serp.parser import ParsedSERPResult, parse_google_serp
from app.utils.geo import build_google_uule
from app.worker.celery_app import celery_app


logger = logging.getLogger(__name__)

RANK_DROP_THRESHOLD = 5
RANK_SPIKE_THRESHOLD = 5


@celery_app.task(
    bind=True,
    name="app.worker.tasks.send_password_reset_email",
    autoretry_for=(Exception,),
    max_retries=3,
    retry_backoff=True,
)
def send_password_reset_email(
    self: object,
    email: str,
    reset_token: str,
) -> dict[str, str]:
    """Send a password-reset email via Resend."""
    del self
    send_password_reset(email=email, reset_token=reset_token)
    return {"email": email, "status": "sent"}


@celery_app.task(
    bind=True,
    name="app.worker.tasks.send_org_invite_email",
    autoretry_for=(Exception,),
    max_retries=3,
    retry_backoff=True,
)
def send_org_invite_email(
    self: object,
    email: str,
    invite_token: str,
    org_name: str,
) -> dict[str, str]:
    """Send an organisation invite email via Resend."""
    del self
    send_org_invite(email=email, invite_token=invite_token, org_name=org_name)
    return {"email": email, "organization": org_name, "status": "sent"}


@celery_app.task(
    bind=True,
    name="app.worker.tasks.send_billing_alert_email",
    autoretry_for=(Exception,),
    max_retries=3,
    retry_backoff=True,
)
def send_billing_alert_email(
    self: object,
    org_id: str,
    reason: str,
) -> dict[str, str]:
    """Fetch the org owner email then send a billing alert via Resend."""
    del self
    owner_email = asyncio.run(_fetch_org_owner_email(org_id))
    if not owner_email:
        logger.warning("No owner email found for org %s — billing alert not sent.", org_id)
        return {"org_id": org_id, "status": "skipped_no_email"}
    org_name = asyncio.run(_fetch_org_name(org_id)) or "your organization"
    send_billing_alert(org_id=owner_email, org_name=org_name, reason=reason)
    return {"org_id": org_id, "status": "sent"}


async def _fetch_org_owner_email(org_id: str) -> str | None:
    """Return the email of the first owner-role member of the organization."""
    async with AsyncSessionLocal() as session:
        membership = await session.scalar(
            select(OrganizationMembership)
            .where(
                OrganizationMembership.organization_id == org_id,
                OrganizationMembership.role == "owner",
            )
            .limit(1)
        )
        if membership is None:
            return None
        user = await session.get(User, membership.user_id)
        return user.email if user else None


async def _fetch_org_name(org_id: str) -> str | None:
    """Return the display name of the organization."""
    async with AsyncSessionLocal() as session:
        org = await session.get(Organization, org_id)
        return org.name if org else None


@celery_app.task(bind=True, name="app.worker.tasks.fetch_serp_data")
def fetch_serp_data(self: object, keyword_id: str) -> dict[str, object]:
    """Fetch, parse, and persist a localized SERP ranking snapshot for a keyword."""
    del self
    return asyncio.run(_fetch_serp_data_async(keyword_id))


def simulate_serp_scrape(keyword_id: str) -> dict[str, object]:
    """Backward-compatible wrapper for the original Stage 1 task entrypoint."""
    return fetch_serp_data(keyword_id)


async def _fetch_serp_data_async(keyword_id: str) -> dict[str, object]:
    """Run the end-to-end ranking acquisition flow inside an async session."""
    logger.info("Starting live SERP scrape for keyword_id=%s", keyword_id)

    async with AsyncSessionLocal() as session:
        keyword = await _load_keyword(session, keyword_id)
        if keyword is None:
            raise ValueError(f"Keyword '{keyword_id}' was not found.")

        applied_uule = _resolve_uule(keyword)
        applied_lat = _decimal_to_float(keyword.target_location.latitude)
        applied_lng = _decimal_to_float(keyword.target_location.longitude)

        ranking_history = RankingHistory(
            keyword_id=keyword.id,
            project_id=keyword.project_id,
            target_location_id=keyword.target_location_id,
            status="running",
            query_keyword=keyword.phrase,
            location_label=keyword.target_location.label,
            uule=applied_uule,
            latitude=keyword.target_location.latitude,
            longitude=keyword.target_location.longitude,
            started_at=datetime.now(timezone.utc),
        )
        session.add(ranking_history)
        await session.commit()
        await session.refresh(ranking_history)

        try:
            client = HTTPGoogleSERPClient()
            fetch_result = await client.fetch_rankings(
                keyword=keyword.phrase,
                uule=applied_uule,
                lat=applied_lat,
                lng=applied_lng,
            )
            parsed_result = parse_google_serp(fetch_result.html)
            await _mark_history_succeeded(session, ranking_history, parsed_result)
        except Exception as exc:
            logger.exception(
                "SERP scrape failed for keyword_id=%s ranking_history_id=%s",
                keyword_id,
                ranking_history.id,
            )
            await session.rollback()
            await _mark_history_failed(session, ranking_history.id, str(exc))
            raise

    logger.info("Finished live SERP scrape for keyword_id=%s", keyword_id)
    return {
        "keyword_id": str(keyword.id),
        "ranking_history_id": str(ranking_history.id),
        "status": "succeeded",
        "organic_results_count": len(parsed_result.organic_results),
        "map_pack_results_count": len(parsed_result.map_pack_results),
    }


async def _load_keyword(session: AsyncSession, keyword_id: str) -> Keyword | None:
    """Load a keyword together with project and location context."""
    keyword_uuid = UUID(keyword_id)
    statement = (
        select(Keyword)
        .options(
            joinedload(Keyword.project),
            joinedload(Keyword.target_location),
        )
        .where(Keyword.id == keyword_uuid)
    )
    return await session.scalar(statement)


async def _mark_history_succeeded(
    session: AsyncSession,
    ranking_history: RankingHistory,
    parsed_result: ParsedSERPResult,
) -> None:
    """Persist successful parse output into the ranking history row."""
    ranking_history.status = "succeeded"
    ranking_history.error_reason = None
    ranking_history.organic_rank = (
        parsed_result.organic_results[0].position if parsed_result.organic_results else None
    )
    ranking_history.map_pack_rank = (
        parsed_result.map_pack_results[0].position if parsed_result.map_pack_results else None
    )
    ranking_history.organic_results = [
        result.model_dump(mode="json") for result in parsed_result.organic_results
    ]
    ranking_history.map_pack_results = [
        result.model_dump(mode="json") for result in parsed_result.map_pack_results
    ]
    ranking_history.completed_at = datetime.now(timezone.utc)
    session.add(ranking_history)
    await session.commit()
    await _check_rank_change(session, ranking_history)


async def _mark_history_failed(
    session: AsyncSession,
    ranking_history_id: UUID,
    error_reason: str,
) -> None:
    """Persist a failed task state and exact failure reason."""
    ranking_history = await session.get(RankingHistory, ranking_history_id)
    if ranking_history is None:
        return

    ranking_history.status = "failed"
    ranking_history.error_reason = error_reason
    ranking_history.completed_at = datetime.now(timezone.utc)
    session.add(ranking_history)
    await session.commit()


def _resolve_uule(keyword: Keyword) -> str | None:
    """Return either a stored UULE or a generated value from location metadata."""
    location = keyword.target_location
    if location.uule:
        return location.uule

    if location.label.strip():
        return build_google_uule(location.label)

    location_parts = [location.city, location.postal_code, location.country_code]
    normalized_parts = [part.strip() for part in location_parts if part and part.strip()]
    if not normalized_parts:
        return None

    return build_google_uule(", ".join(normalized_parts))


def _decimal_to_float(value: Decimal | None) -> float | None:
    """Convert database numeric values into HTTP client primitives."""
    if value is None:
        return None
    return float(value)


async def _check_rank_change(
    session: AsyncSession,
    ranking_history: RankingHistory,
) -> None:
    """Compare new ranking with the previous snapshot and log significant changes."""
    previous = await session.scalar(
        select(RankingHistory)
        .where(
            RankingHistory.keyword_id == ranking_history.keyword_id,
            RankingHistory.status == "succeeded",
            RankingHistory.id != ranking_history.id,
        )
        .order_by(RankingHistory.completed_at.desc().nullslast(), RankingHistory.started_at.desc())
        .limit(1)
    )
    if previous is None:
        return

    new_organic = ranking_history.organic_rank
    prev_organic = previous.organic_rank

    if new_organic is not None and prev_organic is not None:
        delta = new_organic - prev_organic
        if delta >= RANK_DROP_THRESHOLD:
            logger.warning(
                "RANK DROP detected keyword_id=%s phrase=%s location=%s: %d → %d (Δ+%d)",
                ranking_history.keyword_id,
                ranking_history.query_keyword,
                ranking_history.location_label,
                prev_organic,
                new_organic,
                delta,
            )
        elif -delta >= RANK_SPIKE_THRESHOLD:
            logger.info(
                "RANK IMPROVEMENT detected keyword_id=%s phrase=%s location=%s: %d → %d (Δ%d)",
                ranking_history.keyword_id,
                ranking_history.query_keyword,
                ranking_history.location_label,
                prev_organic,
                new_organic,
                delta,
            )


@celery_app.task(bind=True, name="app.worker.tasks.nightly_track_all_keywords")
def nightly_track_all_keywords(self: object) -> dict[str, object]:
    """Queue daily SERP tracking tasks for all active keywords."""
    del self
    return asyncio.run(_nightly_track_all_keywords_async())


async def _nightly_track_all_keywords_async() -> dict[str, object]:
    """Select all active keywords and enqueue a tracking task for each."""
    async with AsyncSessionLocal() as session:
        keyword_ids = (
            await session.scalars(
                select(Keyword.id).where(Keyword.is_active.is_(True))
            )
        ).all()

    queued = 0
    for keyword_id in keyword_ids:
        try:
            fetch_serp_data.delay(str(keyword_id))
            queued += 1
        except Exception:
            logger.exception("Failed to queue SERP task for keyword_id=%s", keyword_id)

    logger.info("Nightly keyword tracking: queued %d tasks", queued)
    return {"queued": queued}
