"""Google Business Profile integration endpoints."""

from __future__ import annotations

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import OrganizationContext, get_current_organization_context
from app.db.session import get_db_session
from app.google.client import GoogleIntegrationError
from app.google.models import GoogleAccount, GoogleBusinessProfile
from app.google.service import GoogleIntegrationService
from app.schemas.auth import MessageResponse
from app.schemas.google import (
    GoogleAccountResponse,
    GoogleBusinessProfileResponse,
    GoogleIntegrationStatusResponse,
    GoogleOAuthCallbackRequest,
    GoogleOAuthConnectResponse,
    GoogleSyncAcceptedResponse,
    ProfileListResponse,
)
from app.schemas.task import TaskStatusResponse
from app.worker.celery_app import celery_app
from app.worker.google_tasks import sync_google_account_task
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


@router.delete("/accounts/{account_id}", response_model=MessageResponse)
async def disconnect_google_account(
    account_id: UUID,
    context: OrganizationContext = Depends(get_current_organization_context),
    db_session: AsyncSession = Depends(get_db_session),
) -> MessageResponse:
    """Disconnect a Google account and remove all associated profiles."""
    if context.membership.role not in {"owner", "admin"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Organization admin access is required.",
        )
    account = await db_session.scalar(
        select(GoogleAccount).where(
            GoogleAccount.id == account_id,
            GoogleAccount.organization_id == context.organization.id,
        )
    )
    if account is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Google account was not found.",
        )
    await db_session.delete(account)
    await db_session.commit()
    return MessageResponse(message="Google account disconnected successfully.")


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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Google account was not found.",
        )

    try:
        task = sync_google_account_task.delay(
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
        message="Sync queued successfully.",
        task_id=task.id,
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


@router.get("/profiles", response_model=ProfileListResponse)
async def list_google_profiles(
    limit: int = 20,
    offset: int = 0,
    context: OrganizationContext = Depends(get_current_organization_context),
    db_session: AsyncSession = Depends(get_db_session),
) -> ProfileListResponse:
    """Return a paginated list of synced Google Business Profiles for the organization."""
    total = int(
        await db_session.scalar(
            select(func.count(GoogleBusinessProfile.id)).where(
                GoogleBusinessProfile.organization_id == context.organization.id
            )
        )
        or 0
    )
    profiles = (
        (
            await db_session.execute(
                select(GoogleBusinessProfile)
                .where(GoogleBusinessProfile.organization_id == context.organization.id)
                .order_by(GoogleBusinessProfile.updated_at.desc())
                .limit(limit)
                .offset(offset)
            )
        )
        .scalars()
        .all()
    )
    return ProfileListResponse(
        profiles=[GoogleBusinessProfileResponse.model_validate(p) for p in profiles],
        total=total,
    )


@router.get("/profiles/{profile_id}", response_model=GoogleBusinessProfileResponse)
async def get_google_profile(
    profile_id: UUID,
    context: OrganizationContext = Depends(get_current_organization_context),
    db_session: AsyncSession = Depends(get_db_session),
) -> GoogleBusinessProfileResponse:
    """Return one synced Google Business Profile by ID."""
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
    return GoogleBusinessProfileResponse.model_validate(profile)
