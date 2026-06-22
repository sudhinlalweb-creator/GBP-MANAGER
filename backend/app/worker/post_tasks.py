"""Celery tasks for publishing scheduled GBP local posts."""

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


@celery_app.task(bind=True, name="app.worker.post_tasks.publish_scheduled_posts")
def publish_scheduled_posts(self: object) -> dict[str, object]:
    """Publish all GBP posts whose scheduled_at time has passed."""
    del self
    return asyncio.run(_publish_scheduled_posts_async())


async def _publish_scheduled_posts_async() -> dict[str, object]:
    from app.google.client import GoogleBusinessProfileClient, GoogleOAuthClient
    from app.google.models import GoogleAccount, GoogleBusinessProfile
    from app.models.post import GBPPost

    now = datetime.now(timezone.utc)

    async with AsyncSessionLocal() as session:
        due_posts = (
            await session.scalars(
                select(GBPPost)
                .options(
                    joinedload(GBPPost.google_profile).joinedload(GoogleBusinessProfile.reviews)
                )
                .where(
                    GBPPost.state == "scheduled",
                    GBPPost.scheduled_at <= now,
                )
            )
        ).all()

        published = 0
        failed = 0

        for post in due_posts:
            try:
                profile = await session.get(GoogleBusinessProfile, post.google_profile_id)
                if profile is None:
                    continue
                account = await session.get(GoogleAccount, profile.google_account_id)
                if account is None or not account.refresh_token_encrypted:
                    continue

                oauth_client = GoogleOAuthClient()
                tokens = await oauth_client.refresh_access_token(account.refresh_token_encrypted)
                access_token = tokens["access_token"]

                post_data: dict = {"summary": post.summary, "topicType": post.post_type}
                if post.call_to_action_type and post.call_to_action_url:
                    post_data["callToAction"] = {
                        "actionType": post.call_to_action_type,
                        "url": post.call_to_action_url,
                    }
                if post.media_url:
                    post_data["media"] = [{"mediaFormat": "PHOTO", "sourceUrl": post.media_url}]

                gbp_client = GoogleBusinessProfileClient()
                result = await gbp_client.create_post(
                    access_token, profile.google_location_name, post_data
                )

                post.google_post_id = result.get("name", "").split("/")[-1]
                post.state = "published"
                post.published_at = now
                post.raw_data = result
                session.add(post)
                published += 1

            except Exception as exc:
                logger.exception("Failed to publish post_id=%s: %s", post.id, exc)
                post.state = "failed"
                post.error_reason = str(exc)
                session.add(post)
                failed += 1

        await session.commit()

    logger.info("Scheduled post publisher: published=%d failed=%d", published, failed)
    return {"published": published, "failed": failed}
