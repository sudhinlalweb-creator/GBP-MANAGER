"""Celery tasks for Google Business Profile synchronization."""

from __future__ import annotations

import asyncio
import logging
from uuid import UUID

from app.db.session import AsyncSessionLocal
from app.google.client import GoogleIntegrationError
from app.google.service import GoogleIntegrationService
from app.worker.celery_app import celery_app


logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="app.worker.google_tasks.sync_google_account_profiles")
def sync_google_account_profiles(
    self: object,
    organization_id: str,
    google_account_id: str,
) -> dict[str, object]:
    """Sync Google Business Profiles for one connected Google account."""
    del self
    return asyncio.run(_sync_google_account_profiles_async(organization_id, google_account_id))


async def _sync_google_account_profiles_async(
    organization_id: str,
    google_account_id: str,
) -> dict[str, object]:
    """Run the Google profile sync inside an async SQLAlchemy session."""
    service = GoogleIntegrationService()
    logger.info(
        "Starting Google sync for organization_id=%s google_account_id=%s",
        organization_id,
        google_account_id,
    )
    async with AsyncSessionLocal() as db_session:
        try:
            result = await service.sync_google_account(
                db_session=db_session,
                organization_id=UUID(organization_id),
                google_account_id=UUID(google_account_id),
            )
        except GoogleIntegrationError:
            logger.exception(
                "Google sync failed for organization_id=%s google_account_id=%s",
                organization_id,
                google_account_id,
            )
            await db_session.rollback()
            raise

    logger.info(
        "Finished Google sync for organization_id=%s google_account_id=%s",
        organization_id,
        google_account_id,
    )
    return result.model_dump(mode="json")
