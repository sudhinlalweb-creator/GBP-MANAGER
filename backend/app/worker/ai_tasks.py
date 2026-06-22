"""Celery tasks for AI audit and scoring workflows."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select

from app.ai.service import AIAuditService
from app.db.session import AsyncSessionLocal
from app.models.user import User
from app.organizations.models import Organization, OrganizationMembership
from app.worker.celery_app import celery_app


logger = logging.getLogger(__name__)


@dataclass
class _TaskOrganizationContext:
    organization: Organization
    membership: OrganizationMembership
    user: User


@celery_app.task(bind=True, name="app.worker.ai_tasks.run_ai_audit")
def run_ai_audit(self: object, organization_id: str, user_id: str) -> dict[str, object]:
    """Run an AI audit asynchronously for the specified organization and user."""
    del self
    return asyncio.run(_run_ai_audit_async(organization_id, user_id))


async def _run_ai_audit_async(organization_id: str, user_id: str) -> dict[str, object]:
    """Execute the heuristic AI audit inside an async database session."""
    logger.info("Starting AI audit for organization_id=%s user_id=%s", organization_id, user_id)
    async with AsyncSessionLocal() as db_session:
        context = await _load_context(
            db_session=db_session,
            organization_id=UUID(organization_id),
            user_id=UUID(user_id),
        )
        if context is None:
            raise ValueError("Unable to resolve organization context for the AI audit task.")

        service = AIAuditService()
        summary = await service.build_summary(db_session, context)

    logger.info("Finished AI audit for organization_id=%s user_id=%s", organization_id, user_id)
    return summary.model_dump(mode="json")


async def _load_context(
    db_session,
    organization_id: UUID,
    user_id: UUID,
) -> _TaskOrganizationContext | None:
    user = await db_session.get(User, user_id)
    organization = await db_session.get(Organization, organization_id)
    membership = await db_session.scalar(
        select(OrganizationMembership).where(
            OrganizationMembership.organization_id == organization_id,
            OrganizationMembership.user_id == user_id,
        )
    )
    if user is None or organization is None or membership is None:
        return None

    return _TaskOrganizationContext(
        organization=organization,
        membership=membership,
        user=user,
    )
