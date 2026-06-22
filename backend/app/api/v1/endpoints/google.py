"""Google Business Profile integration endpoints."""

from __future__ import annotations

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import OrganizationContext, get_current_organization_context
from app.db.session import get_db_session
from app.google.client import GoogleIntegrationError
from app.google.models import GoogleAccount
from app.google.service import GoogleIntegrationService
from app.schemas.google import (
    GoogleAccountResponse,
    GoogleIntegrationStatusResponse,
    GoogleOAuthCallbackRequest,
    GoogleOAuthConnectResponse,
    GoogleSyncAcceptedResponse,
)
from app.schemas.task import TaskStatusResponse
from app.worker.celery_app import celery_app
from app.worker.google_tasks import sync_google_account_profiles
from celery.result import AsyncResult


logger = logging.getLogger(__name__)
router = APIRouter()
service = GoogleIntegrationService()


@router.get("/status", response_model=GoogleIntegrationStatusResponse)
async def get_google_status(
    context: OrganizationContext = Depends(get_current_organization_context),
    db_session: AsyncSession = Depends(get_db_session),
) -> GoogleIntegrationStatusResponse:
    """Return Google integration readiness for the current organization."""
    return await service.get_integration_status(db_session, context)


@router.get("/connect", response_model=GoogleOAuthConnectResponse)
async def build_google_connect_url(
    context: OrganizationContext = Depends(get_current_organization_context),
) -> GoogleOAuthConnectResponse:
    """Return a Google OAuth URL for the authenticated organization."""
    try:
        return service.build_connect_response(context)
    except GoogleIntegrationError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc


@router.post("/callback", response_model=GoogleAccountResponse)
async def connect_google_account(
    payload: GoogleOAuthCallbackRequest,
    context: OrganizationContext = Depends(get_current_organization_context),
    db_session: AsyncSession = Depends(get_db_session),
) -> GoogleAccountResponse:
    """Exchange a Google OAuth callback payload and persist the account."""
    try:
        return await service.exchange_callback(
            db_session=db_session,
            context=context,
            code=payload.code,
            state=payload.state,
        )
    except GoogleIntegrationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/accounts", response_model=list[GoogleAccountResponse])
async def list_google_accounts(
    context: OrganizationContext = Depends(get_current_organization_context),
    db_session: AsyncSession = Depends(get_db_session),
) -> list[GoogleAccountResponse]:
    """List connected Google accounts for the active organization."""
    statement = (
        select(GoogleAccount)
        .where(GoogleAccount.organization_id == context.organization.id)
        .order_by(GoogleAccount.created_at.desc())
    )
    accounts = (await db_session.execute(statement)).scalars().all()
    return [GoogleAccountResponse.model_validate(account) for account in accounts]


@router.post(
    "/accounts/{google_account_id}/sync",
    response_model=GoogleSyncAcceptedResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def enqueue_google_account_sync(
    google_account_id: UUID,
    context: OrganizationContext = Depends(get_current_organization_context),
    db_session: AsyncSession = Depends(get_db_session),
) -> GoogleSyncAcceptedResponse:
    """Queue a Celery sync job for a connected Google account."""
    google_account = await db_session.scalar(
        select(GoogleAccount).where(
            GoogleAccount.id == google_account_id,
            GoogleAccount.organization_id == context.organization.id,
        )
    )
    if google_account is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Google account was not found.")

    try:
        task = sync_google_account_profiles.delay(
            str(context.organization.id),
            str(google_account_id),
        )
    except Exception as exc:
        logger.exception(
            "Unable to queue Google sync for organization_id=%s google_account_id=%s",
            context.organization.id,
            google_account_id,
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Background worker is currently unavailable.",
        ) from exc

    return GoogleSyncAcceptedResponse(
        task_id=task.id,
        status="queued",
        google_account_id=google_account_id,
    )


@router.get("/sync/{task_id}", response_model=TaskStatusResponse)
async def get_google_sync_task_status(task_id: str) -> TaskStatusResponse:
    """Return the current state of a queued Google sync task."""
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
