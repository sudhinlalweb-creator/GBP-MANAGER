"""Celery tasks for Google Business Profile synchronization."""

from __future__ import annotations

import asyncio
import logging
from uuid import UUID

from sqlalchemy import select

from app.db.session import AsyncSessionLocal
from app.google.client import GoogleIntegrationError
from app.google.models import GoogleAccount
from app.google.service import GoogleIntegrationService
from app.worker.celery_app import celery_app


logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="app.worker.google_tasks.sync_google_account_task")
def sync_google_account_task(
    self: object,
    organization_id: str,
    google_account_id: str,
) -> dict[str, object]:
    """Sync Google Business Profiles for one connected Google account."""
    del self
    return asyncio.run(_sync_async(organization_id, google_account_id))


async def _sync_async(
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
    return {
        "organization_id": organization_id,
        "google_account_id": google_account_id,
        "accounts_fetched": result.accounts_fetched,
        "profiles_synced": result.profiles_synced,
    }


@celery_app.task(bind=True, name="app.worker.google_tasks.nightly_sync_all_accounts")
def nightly_sync_all_accounts(self: object) -> dict[str, int]:
    """Enqueue individual sync tasks for every connected Google account."""
    del self
    return asyncio.run(_nightly_sync_async())


async def _nightly_sync_async() -> dict[str, int]:
    """Queue a sync task for every connected Google account."""
    accounts_queued = 0
    async with AsyncSessionLocal() as db_session:
        accounts = (
            (await db_session.execute(select(GoogleAccount)))
            .scalars()
            .all()
        )
        for account in accounts:
            celery_app.send_task(
                "app.worker.google_tasks.sync_google_account_task",
                kwargs={
                    "organization_id": str(account.organization_id),
                    "google_account_id": str(account.id),
                },
            )
            accounts_queued += 1
    return {"accounts_queued": accounts_queued}
