"""AI audit endpoints for SEO score, business health, and recommendation generation."""

from __future__ import annotations

import logging

from celery.result import AsyncResult
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.service import AIAuditService
from app.api.deps import OrganizationContext, get_current_organization_context
from app.db.session import get_db_session
from app.schemas.audit import AuditSummaryResponse, ScoreResponse
from app.schemas.task import TaskAcceptedResponse, TaskStatusResponse
from app.worker.ai_tasks import run_ai_audit
from app.worker.celery_app import celery_app


logger = logging.getLogger(__name__)
router = APIRouter()
service = AIAuditService()


@router.get("/summary", response_model=AuditSummaryResponse)
async def get_audit_summary(
    context: OrganizationContext = Depends(get_current_organization_context),
    db_session: AsyncSession = Depends(get_db_session),
) -> AuditSummaryResponse:
    """Return the current organization audit summary."""
    return await service.build_summary(db_session, context)


@router.get("/seo-score", response_model=ScoreResponse)
async def get_seo_score(
    context: OrganizationContext = Depends(get_current_organization_context),
    db_session: AsyncSession = Depends(get_db_session),
) -> ScoreResponse:
    """Return the SEO score for the active organization context."""
    return await service.get_seo_score(db_session, context)


@router.get("/business-health", response_model=ScoreResponse)
async def get_business_health_score(
    context: OrganizationContext = Depends(get_current_organization_context),
    db_session: AsyncSession = Depends(get_db_session),
) -> ScoreResponse:
    """Return the business health score for the active organization context."""
    return await service.get_business_health_score(db_session, context)


@router.post("/run", response_model=TaskAcceptedResponse, status_code=status.HTTP_202_ACCEPTED)
async def enqueue_ai_audit(
    context: OrganizationContext = Depends(get_current_organization_context),
) -> TaskAcceptedResponse:
    """Queue a non-blocking AI audit run for the active organization."""
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
