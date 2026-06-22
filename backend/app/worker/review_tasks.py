"""Celery tasks for syncing GBP reviews and triggering auto-reply automation."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.db.session import AsyncSessionLocal
from app.worker.celery_app import celery_app


logger = logging.getLogger(__name__)

_STAR_RATING_MAP = {
    "ONE": 1,
    "TWO": 2,
    "THREE": 3,
    "FOUR": 4,
    "FIVE": 5,
}


@celery_app.task(bind=True, name="app.worker.review_tasks.sync_profile_reviews")
def sync_profile_reviews(self: object, google_profile_id: str) -> dict[str, object]:
    """Sync reviews for a single GBP profile from the Google API."""
    del self
    return asyncio.run(_sync_profile_reviews_async(google_profile_id))


async def _sync_profile_reviews_async(google_profile_id: str) -> dict[str, object]:
    from app.google.client import GoogleBusinessProfileClient, GoogleOAuthClient
    from app.google.models import GoogleAccount, GoogleBusinessProfile
    from app.models.automation import AutomationRule
    from app.models.review import GBPReview

    async with AsyncSessionLocal() as session:
        profile = await session.scalar(
            select(GoogleBusinessProfile)
            .options(joinedload(GoogleBusinessProfile.reviews))
            .where(GoogleBusinessProfile.id == UUID(google_profile_id))
        )
        if profile is None:
            raise ValueError(f"Profile '{google_profile_id}' not found.")

        account = await session.get(GoogleAccount, profile.google_account_id)
        if account is None or not account.refresh_token_encrypted:
            raise ValueError("Google account or refresh token not found.")

        oauth_client = GoogleOAuthClient()
        tokens = await oauth_client.refresh_access_token(account.refresh_token_encrypted)
        access_token = tokens["access_token"]

        gbp_client = GoogleBusinessProfileClient()
        raw_reviews = await gbp_client.fetch_reviews(access_token, profile.google_location_name)

        existing_ids = {r.google_review_id for r in profile.reviews}
        new_count = 0
        updated_count = 0

        for raw in raw_reviews:
            review_id = raw.get("reviewId", "")
            rating_str = raw.get("starRating", "")
            rating = _STAR_RATING_MAP.get(rating_str)
            sentiment = _classify_sentiment(rating)
            review_time_str = raw.get("createTime")
            review_time = _parse_google_time(review_time_str)
            reply_comment = raw.get("reviewReply", {}).get("comment")
            reply_time_str = raw.get("reviewReply", {}).get("updateTime")

            if review_id in existing_ids:
                existing = next(r for r in profile.reviews if r.google_review_id == review_id)
                existing.reply_text = reply_comment
                if reply_time_str:
                    existing.replied_at = _parse_google_time(reply_time_str)
                existing.raw_data = raw
                session.add(existing)
                updated_count += 1
            else:
                review = GBPReview(
                    google_profile_id=profile.id,
                    google_review_id=review_id,
                    author_name=raw.get("reviewer", {}).get("displayName"),
                    author_photo_url=raw.get("reviewer", {}).get("profilePhotoUrl"),
                    rating=rating,
                    comment=raw.get("comment"),
                    review_time=review_time,
                    reply_text=reply_comment,
                    replied_at=_parse_google_time(reply_time_str) if reply_time_str else None,
                    sentiment=sentiment,
                    raw_data=raw,
                )
                session.add(review)
                new_count += 1

                # Check automation rules for auto-reply
                await _maybe_auto_reply(
                    session, profile, review, access_token, gbp_client
                )

        await session.commit()

    logger.info(
        "Review sync complete for profile_id=%s new=%d updated=%d",
        google_profile_id,
        new_count,
        updated_count,
    )
    return {"profile_id": google_profile_id, "new": new_count, "updated": updated_count}


async def _maybe_auto_reply(
    session,
    profile,
    review: "GBPReview",
    access_token: str,
    gbp_client: "GoogleBusinessProfileClient",
) -> None:
    """Check automation rules and post an auto-reply if a matching rule exists."""
    from app.models.automation import AutomationRule

    rule_type = f"auto_reply_{review.sentiment or 'neutral'}"
    rule = await session.scalar(
        select(AutomationRule).where(
            AutomationRule.organization_id == profile.organization_id,
            AutomationRule.rule_type == rule_type,
            AutomationRule.is_active.is_(True),
        )
        .limit(1)
    )
    if rule is None or not rule.config:
        return

    template: str = rule.config.get("template", "")
    if not template:
        return

    reply_text = template.replace("{{author}}", review.author_name or "there")

    try:
        await gbp_client.reply_to_review(
            access_token,
            profile.google_location_name,
            review.google_review_id,
            reply_text,
        )
        review.reply_text = reply_text
        review.replied_at = datetime.now(timezone.utc)
        session.add(review)
        logger.info(
            "Auto-reply posted for review_id=%s rule_type=%s", review.google_review_id, rule_type
        )
    except Exception:
        logger.exception(
            "Auto-reply failed for review_id=%s", review.google_review_id
        )


@celery_app.task(bind=True, name="app.worker.review_tasks.nightly_sync_all_reviews")
def nightly_sync_all_reviews(self: object) -> dict[str, object]:
    """Queue review sync tasks for all active GBP profiles."""
    del self
    return asyncio.run(_nightly_sync_all_reviews_async())


async def _nightly_sync_all_reviews_async() -> dict[str, object]:
    from app.google.models import GoogleBusinessProfile

    async with AsyncSessionLocal() as session:
        profile_ids = (
            await session.scalars(
                select(GoogleBusinessProfile.id).where(
                    GoogleBusinessProfile.is_disconnected.is_(False),
                    GoogleBusinessProfile.is_suspended.is_(False),
                )
            )
        ).all()

    queued = 0
    for profile_id in profile_ids:
        try:
            sync_profile_reviews.delay(str(profile_id))
            queued += 1
        except Exception:
            logger.exception("Failed to queue review sync for profile_id=%s", profile_id)

    logger.info("Nightly review sync: queued %d tasks", queued)
    return {"queued": queued}


def _classify_sentiment(rating: int | None) -> str:
    if rating is None:
        return "neutral"
    if rating >= 4:
        return "positive"
    if rating <= 2:
        return "negative"
    return "neutral"


def _parse_google_time(time_str: str | None) -> datetime | None:
    if not time_str:
        return None
    try:
        return datetime.fromisoformat(time_str.replace("Z", "+00:00"))
    except ValueError:
        return None
