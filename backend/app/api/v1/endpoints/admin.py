"""Read-only admin endpoints for the SaaS control center."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.admin.service import AdminService
from app.api.deps import get_current_superuser
from app.db.session import get_db_session
from app.models.user import User
from app.schemas.admin import (
    AdminDashboardResponse,
    AdminOrganizationItem,
    AdminOrganizationTierUpdateRequest,
    AdminUserItem,
    AdminUserStatusUpdateRequest,
)


router = APIRouter()
service = AdminService()


@router.get("/summary", response_model=AdminDashboardResponse)
async def get_admin_dashboard_summary(
    current_user: User = Depends(get_current_superuser),
    db_session: AsyncSession = Depends(get_db_session),
) -> AdminDashboardResponse:
    """Return the aggregated admin dashboard payload for superusers."""
    del current_user
    return await service.get_dashboard(db_session)


@router.patch("/users/{user_id}", response_model=AdminUserItem)
async def update_admin_user_status(
    user_id: UUID,
    payload: AdminUserStatusUpdateRequest,
    current_user: User = Depends(get_current_superuser),
    db_session: AsyncSession = Depends(get_db_session),
) -> AdminUserItem:
    """Activate or suspend a user from the admin console."""
    try:
        return await service.update_user_status(
            db_session,
            actor=current_user,
            user_id=user_id,
            payload=payload,
        )
    except PermissionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.patch("/organizations/{organization_id}", response_model=AdminOrganizationItem)
async def update_admin_organization_tier(
    organization_id: UUID,
    payload: AdminOrganizationTierUpdateRequest,
    current_user: User = Depends(get_current_superuser),
    db_session: AsyncSession = Depends(get_db_session),
) -> AdminOrganizationItem:
    """Update one organization's subscription tier."""
    del current_user
    try:
        return await service.update_organization_tier(
            db_session,
            organization_id=organization_id,
            payload=payload,
        )
    except ValueError as exc:
        detail = str(exc)
        status_code = 400 if "Unsupported" in detail else 404
        raise HTTPException(status_code=status_code, detail=detail) from exc
