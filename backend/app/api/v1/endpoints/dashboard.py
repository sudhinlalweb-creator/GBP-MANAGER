"""Dashboard endpoints for Google Business Profile visibility and sync state."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import OrganizationContext, get_current_organization_context
from app.db.session import get_db_session
from app.google.service import GoogleIntegrationService
from app.schemas.google import GoogleDashboardResponse


router = APIRouter()
service = GoogleIntegrationService()


@router.get("/gbp", response_model=GoogleDashboardResponse)
async def get_google_dashboard(
    context: OrganizationContext = Depends(get_current_organization_context),
    db_session: AsyncSession = Depends(get_db_session),
) -> GoogleDashboardResponse:
    """Return the Phase 2 Google Business Profile dashboard summary."""
    return await service.get_dashboard(db_session, context)
