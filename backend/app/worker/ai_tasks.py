"""Celery tasks for AI audit and scoring workflows."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

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


# ── Per-profile AI audit task ─────────────────────────────────────────────────

@celery_app.task(bind=True, name="app.worker.ai_tasks.run_gbp_audit")
def run_gbp_audit(
    self: object,
    organization_id: str,
    google_profile_id: str,
    requested_by_user_id: str,
    audit_report_id: str,
) -> dict[str, object]:
    """Run an AI GBP audit and persist results to the audit_reports table."""
    del self
    return asyncio.run(
        _run_gbp_audit_async(
            organization_id,
            google_profile_id,
            requested_by_user_id,
            audit_report_id,
        )
    )


async def _run_gbp_audit_async(
    organization_id: str,
    google_profile_id: str,
    requested_by_user_id: str,
    audit_report_id: str,
) -> dict[str, object]:
    """Execute the AI audit inside an async session using the pre-created report row."""
    from app.ai.audit_service import AuditService
    from app.models.audit import AuditReport
    from datetime import datetime, timezone

    logger.info(
        "Starting AI GBP audit for profile_id=%s report_id=%s",
        google_profile_id,
        audit_report_id,
    )

    service = AuditService()
    async with AsyncSessionLocal() as db:
        report = await db.get(AuditReport, UUID(audit_report_id))
        if report is None:
            raise ValueError(f"AuditReport '{audit_report_id}' was not found.")

        report.status = "running"
        report.started_at = datetime.now(timezone.utc)
        db.add(report)
        await db.commit()

        try:
            from app.google.models import GoogleBusinessProfile
            from app.ai.visibility_scoring import (
                compute_engagement_score,
                compute_review_score,
                compute_visibility_score,
            )
            from app.google.scoring import compute_completeness_score
            from app.ai.audit_prompts import build_audit_system_prompt, build_audit_user_prompt
            from app.ai.audit_service import _build_profile_snapshot, _call_ai
            from sqlalchemy import select

            profile = await db.scalar(
                select(GoogleBusinessProfile).where(
                    GoogleBusinessProfile.id == UUID(google_profile_id)
                )
            )
            if profile is None:
                raise ValueError(f"GoogleBusinessProfile '{google_profile_id}' was not found.")

            completeness = compute_completeness_score(profile)
            review_score = compute_review_score(profile.review_count, profile.average_rating)
            engagement_score = compute_engagement_score(profile.total_photos)
            visibility_score = compute_visibility_score(completeness, review_score, engagement_score)
            snapshot = _build_profile_snapshot(profile, completeness, visibility_score)
            provider, model, raw_response, recommendations = await _call_ai(snapshot)

            report.completeness_score = completeness
            report.review_score = review_score
            report.engagement_score = engagement_score
            report.visibility_score = visibility_score
            report.ai_provider = provider
            report.ai_model = model
            report.raw_ai_response = {"response_text": raw_response}
            report.recommendations = recommendations
            report.status = "completed"
            report.completed_at = datetime.now(timezone.utc)

        except Exception as exc:
            logger.exception(
                "AI audit failed for profile_id=%s report_id=%s", google_profile_id, audit_report_id
            )
            report.status = "failed"
            report.error_reason = str(exc)
            report.completed_at = datetime.now(timezone.utc)

        db.add(report)
        await db.commit()

    logger.info(
        "Finished AI GBP audit for profile_id=%s report_id=%s status=%s",
        google_profile_id,
        audit_report_id,
        report.status,
    )
    return {
        "audit_report_id": audit_report_id,
        "google_profile_id": google_profile_id,
        "status": report.status,
        "visibility_score": report.visibility_score,
    }
