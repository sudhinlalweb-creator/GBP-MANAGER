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

from app.db.session import AsyncSessionLocal
from app.models.keyword import Keyword
from app.models.ranking_history import RankingHistory
from app.services.serp.client import HTTPGoogleSERPClient
from app.services.serp.parser import ParsedSERPResult, parse_google_serp
from app.utils.geo import build_google_uule
from app.worker.celery_app import celery_app


logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="app.worker.tasks.send_password_reset_email")
def send_password_reset_email(
    self: object,
    email: str,
    reset_token: str,
) -> dict[str, str]:
    """Log a password reset email payload for later provider integration."""
    del self
    logger.info(
        "Queued password reset email for %s with token prefix %s",
        email,
        reset_token[:12],
    )
    return {"email": email, "status": "queued"}


@celery_app.task(bind=True, name="app.worker.tasks.send_org_invite_email")
def send_org_invite_email(
    self: object,
    email: str,
    invite_token: str,
    org_name: str,
) -> dict[str, str]:
    """Log an organization invite email payload for later provider integration."""
    del self
    logger.info(
        "Queued organization invite email for %s into %s with token prefix %s",
        email,
        org_name,
        invite_token[:12],
    )
    return {"email": email, "organization": org_name, "status": "queued"}


@celery_app.task(bind=True, name="app.worker.tasks.send_billing_alert_email")
def send_billing_alert_email(
    self: object,
    org_id: str,
    reason: str,
) -> dict[str, str]:
    """Log a billing alert payload for later provider integration."""
    del self
    logger.info("Queued billing alert for org %s reason=%s", org_id, reason)
    return {"org_id": org_id, "status": "queued"}


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
