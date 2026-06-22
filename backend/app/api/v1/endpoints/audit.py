"""AI audit endpoints for SEO score, business health, and per-profile audit reports."""

from __future__ import annotations

import logging
from uuid import UUID

from celery.result import AsyncResult
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.audit_service import AuditService
from app.ai.service import AIAuditService
from app.api.deps import OrganizationContext, get_current_organization_context, require_plan
from app.db.session import get_db_session
from app.schemas.audit import (
    AuditReportListResponse,
    AuditReportResponse,
    AuditReportSummaryResponse,
    AuditScoreResponse,
    AuditSummaryResponse,
    ScoreResponse,
)
from app.schemas.task import TaskAcceptedResponse, TaskStatusResponse
from app.worker.ai_tasks import run_gbp_audit
from app.worker.celery_app import celery_app


logger = logging.getLogger(__name__)
router = APIRouter()
heuristic_service = AIAuditService()
audit_service = AuditService()


# ── Org-level heuristic audit ─────────────────────────────────────────────────

@router.get("/summary", response_model=AuditSummaryResponse)
async def get_audit_summary(
    context: OrganizationContext = Depends(get_current_organization_context),
    db_session: AsyncSession = Depends(get_db_session),
) -> AuditSummaryResponse:
    """Return the current organization audit summary."""
    return await heuristic_service.build_summary(db_session, context)


@router.get("/seo-score", response_model=ScoreResponse)
async def get_seo_score(
    context: OrganizationContext = Depends(get_current_organization_context),
    db_session: AsyncSession = Depends(get_db_session),
) -> ScoreResponse:
    """Return the SEO score for the active organization context."""
    return await heuristic_service.get_seo_score(db_session, context)


@router.get("/business-health", response_model=ScoreResponse)
async def get_business_health_score(
    context: OrganizationContext = Depends(get_current_organization_context),
    db_session: AsyncSession = Depends(get_db_session),
) -> ScoreResponse:
    """Return the business health score for the active organization context."""
    return await heuristic_service.get_business_health_score(db_session, context)


# ── Per-profile AI audit ──────────────────────────────────────────────────────

@router.post(
    "/profiles/{profile_id}/run",
    response_model=AuditReportSummaryResponse,
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(require_plan("starter"))],
)
async def enqueue_profile_audit(
    profile_id: UUID,
    context: OrganizationContext = Depends(get_current_organization_context),
    db_session: AsyncSession = Depends(get_db_session),
) -> AuditReportSummaryResponse:
    """Queue an AI audit for one Google Business Profile."""
    from app.models.audit import AuditReport
    from app.google.models import GoogleBusinessProfile
    from sqlalchemy import select
    from datetime import datetime, timezone

    profile = await db_session.scalar(
        select(GoogleBusinessProfile).where(
            GoogleBusinessProfile.id == profile_id,
            GoogleBusinessProfile.organization_id == context.organization.id,
        )
    )
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Google Business Profile was not found.",
        )

    await audit_service._enforce_cooldown(db_session, profile_id)

    report = AuditReport(
        organization_id=context.organization.id,
        google_profile_id=profile_id,
        requested_by_user_id=context.user.id,
        status="pending",
    )
    db_session.add(report)
    await db_session.commit()
    await db_session.refresh(report)

    try:
        run_gbp_audit.delay(
            str(context.organization.id),
            str(profile_id),
            str(context.user.id),
            str(report.id),
        )
    except Exception as exc:
        logger.exception("Unable to queue audit for profile_id=%s", profile_id)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Background worker is currently unavailable.",
        ) from exc

    return AuditReportSummaryResponse.model_validate(report)


@router.get("/profiles/{profile_id}/reports", response_model=AuditReportListResponse)
async def list_profile_audit_reports(
    profile_id: UUID,
    limit: int = 20,
    offset: int = 0,
    context: OrganizationContext = Depends(get_current_organization_context),
    db_session: AsyncSession = Depends(get_db_session),
) -> AuditReportListResponse:
    """Return paginated audit reports for one profile."""
    reports, total = await audit_service.list_reports(
        db=db_session,
        organization_id=context.organization.id,
        google_profile_id=profile_id,
        limit=limit,
        offset=offset,
    )
    return AuditReportListResponse(
        reports=[AuditReportSummaryResponse.model_validate(r) for r in reports],
        total=total,
    )


@router.get("/reports/{report_id}", response_model=AuditReportResponse)
async def get_audit_report(
    report_id: UUID,
    context: OrganizationContext = Depends(get_current_organization_context),
    db_session: AsyncSession = Depends(get_db_session),
) -> AuditReportResponse:
    """Return one full audit report including recommendations."""
    report = await audit_service.get_report(
        db=db_session,
        organization_id=context.organization.id,
        report_id=report_id,
    )
    return AuditReportResponse.model_validate(report)


@router.get("/reports/{report_id}/score", response_model=AuditScoreResponse)
async def get_audit_report_score(
    report_id: UUID,
    context: OrganizationContext = Depends(get_current_organization_context),
    db_session: AsyncSession = Depends(get_db_session),
) -> AuditScoreResponse:
    """Return the score breakdown for one completed audit report."""
    report = await audit_service.get_report(
        db=db_session,
        organization_id=context.organization.id,
        report_id=report_id,
    )
    return AuditScoreResponse(
        report_id=report.id,
        visibility_score=report.visibility_score,
        completeness_score=report.completeness_score,
        review_score=report.review_score,
        engagement_score=report.engagement_score,
        score_breakdown={
            "completeness_weight": 0.40,
            "reviews_weight": 0.40,
            "engagement_weight": 0.20,
        },
    )


# ── Legacy task-based run endpoint ────────────────────────────────────────────

@router.post("/run", response_model=TaskAcceptedResponse, status_code=status.HTTP_202_ACCEPTED)
async def enqueue_ai_audit(
    context: OrganizationContext = Depends(get_current_organization_context),
) -> TaskAcceptedResponse:
    """Queue a non-blocking heuristic audit run for the active organization."""
    from app.worker.ai_tasks import run_ai_audit

    try:
        task = run_ai_audit.delay(str(context.organization.id), str(context.user.id))
    except Exception as exc:
        logger.exception("Unable to queue AI audit for organization_id=%s", context.organization.id)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Background worker is currently unavailable.",
        ) from exc

    return TaskAcceptedResponse(task_id=task.id, status="queued")


@router.get("/tasks/{task_id}", response_model=TaskStatusResponse)
async def get_ai_audit_task_status(task_id: str) -> TaskStatusResponse:
    """Return the current state of a queued AI audit task."""
    task_result = AsyncResult(task_id, app=celery_app)
    state = task_result.state.lower()

    if state == "failure":
        return TaskStatusResponse(task_id=task_id, status=state, error=str(task_result.result))

    if state == "success":
        result = task_result.result
        return TaskStatusResponse(
            task_id=task_id,
            status=state,
            result=result if isinstance(result, dict) else {"result": str(result)},
        )

    return TaskStatusResponse(task_id=task_id, status=state)
