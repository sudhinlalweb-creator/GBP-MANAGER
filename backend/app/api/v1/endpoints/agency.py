"""Agency white-label branding, client management, and shareable report endpoints."""

from __future__ import annotations

import secrets
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import OrganizationContext, get_current_organization_context, require_plan
from app.db.session import get_db_session
from app.google.models import GoogleBusinessProfile
from app.models.agency import AgencyBranding, AgencyClientLink
from app.models.audit import AuditReport
from app.models.review import GBPReview
from app.organizations.models import Organization
from app.schemas.agency import (
    AddClientRequest,
    AgencyBrandingResponse,
    AgencyBrandingUpdateRequest,
    AgencyDashboardClientSummary,
    AgencyDashboardResponse,
    ClientLinkResponse,
    ShareableReportResponse,
    ShareableReportTokenResponse,
)


router = APIRouter()
_AGENCY_DEP = [Depends(require_plan("agency"))]


# ── White-label branding ──────────────────────────────────────────────────────

@router.get(
    "/branding",
    response_model=AgencyBrandingResponse,
    dependencies=_AGENCY_DEP,
)
async def get_branding(
    context: OrganizationContext = Depends(get_current_organization_context),
    db: AsyncSession = Depends(get_db_session),
) -> AgencyBrandingResponse:
    """Return the white-label branding settings for the agency org."""
    branding = await _get_or_create_branding(db, context.organization.id)
    return AgencyBrandingResponse.model_validate(branding)


@router.patch(
    "/branding",
    response_model=AgencyBrandingResponse,
    dependencies=_AGENCY_DEP,
)
async def update_branding(
    payload: AgencyBrandingUpdateRequest,
    context: OrganizationContext = Depends(get_current_organization_context),
    db: AsyncSession = Depends(get_db_session),
) -> AgencyBrandingResponse:
    """Update white-label branding settings."""
    branding = await _get_or_create_branding(db, context.organization.id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(branding, field, value)
    db.add(branding)
    await db.commit()
    await db.refresh(branding)
    return AgencyBrandingResponse.model_validate(branding)


# ── Client management ─────────────────────────────────────────────────────────

@router.get(
    "/clients",
    response_model=list[ClientLinkResponse],
    dependencies=_AGENCY_DEP,
)
async def list_clients(
    context: OrganizationContext = Depends(get_current_organization_context),
    db: AsyncSession = Depends(get_db_session),
) -> list[ClientLinkResponse]:
    """Return all client organizations managed by this agency."""
    links = (
        await db.scalars(
            select(AgencyClientLink).where(
                AgencyClientLink.agency_org_id == context.organization.id,
                AgencyClientLink.is_active.is_(True),
            )
        )
    ).all()

    result = []
    for link in links:
        client_org = await db.get(Organization, link.client_org_id)
        if client_org:
            result.append(
                ClientLinkResponse(
                    id=link.id,
                    agency_org_id=link.agency_org_id,
                    client_org_id=link.client_org_id,
                    client_org_name=client_org.name,
                    client_org_plan=client_org.plan,
                    is_active=link.is_active,
                    linked_at=link.created_at,
                )
            )
    return result


@router.post(
    "/clients",
    response_model=ClientLinkResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=_AGENCY_DEP,
)
async def add_client(
    payload: AddClientRequest,
    context: OrganizationContext = Depends(get_current_organization_context),
    db: AsyncSession = Depends(get_db_session),
) -> ClientLinkResponse:
    """Link a client organization to this agency."""
    if payload.client_org_id == context.organization.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An agency cannot manage itself.",
        )

    client_org = await db.get(Organization, payload.client_org_id)
    if client_org is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client organization not found.")

    existing = await db.scalar(
        select(AgencyClientLink).where(
            AgencyClientLink.agency_org_id == context.organization.id,
            AgencyClientLink.client_org_id == payload.client_org_id,
        )
    )
    if existing:
        if not existing.is_active:
            existing.is_active = True
            db.add(existing)
            await db.commit()
            await db.refresh(existing)
        return ClientLinkResponse(
            id=existing.id,
            agency_org_id=existing.agency_org_id,
            client_org_id=existing.client_org_id,
            client_org_name=client_org.name,
            client_org_plan=client_org.plan,
            is_active=existing.is_active,
            linked_at=existing.created_at,
        )

    link = AgencyClientLink(
        agency_org_id=context.organization.id,
        client_org_id=payload.client_org_id,
    )
    db.add(link)
    await db.commit()
    await db.refresh(link)

    return ClientLinkResponse(
        id=link.id,
        agency_org_id=link.agency_org_id,
        client_org_id=link.client_org_id,
        client_org_name=client_org.name,
        client_org_plan=client_org.plan,
        is_active=link.is_active,
        linked_at=link.created_at,
    )


@router.delete("/clients/{client_org_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=_AGENCY_DEP)
async def remove_client(
    client_org_id: UUID,
    context: OrganizationContext = Depends(get_current_organization_context),
    db: AsyncSession = Depends(get_db_session),
) -> Response:
    """Unlink a client organization from this agency."""
    link = await db.scalar(
        select(AgencyClientLink).where(
            AgencyClientLink.agency_org_id == context.organization.id,
            AgencyClientLink.client_org_id == client_org_id,
        )
    )
    if link is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client link not found.")
    link.is_active = False
    db.add(link)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ── Agency dashboard ──────────────────────────────────────────────────────────

@router.get("/dashboard", response_model=AgencyDashboardResponse, dependencies=_AGENCY_DEP)
async def get_agency_dashboard(
    context: OrganizationContext = Depends(get_current_organization_context),
    db: AsyncSession = Depends(get_db_session),
) -> AgencyDashboardResponse:
    """Return aggregate metrics across all managed client organizations."""
    client_org_ids = (
        await db.scalars(
            select(AgencyClientLink.client_org_id).where(
                AgencyClientLink.agency_org_id == context.organization.id,
                AgencyClientLink.is_active.is_(True),
            )
        )
    ).all()

    summaries: list[AgencyDashboardClientSummary] = []
    total_locations = 0

    for org_id in client_org_ids:
        client_org = await db.get(Organization, org_id)
        if client_org is None:
            continue

        location_count = await db.scalar(
            select(func.count(GoogleBusinessProfile.id)).where(
                GoogleBusinessProfile.organization_id == org_id,
                GoogleBusinessProfile.is_disconnected.is_(False),
            )
        ) or 0
        total_locations += location_count

        avg_score = await db.scalar(
            select(func.avg(GoogleBusinessProfile.completeness_score)).where(
                GoogleBusinessProfile.organization_id == org_id,
                GoogleBusinessProfile.completeness_score.is_not(None),
            )
        )

        open_reviews = await db.scalar(
            select(func.count(GBPReview.id))
            .join(GoogleBusinessProfile, GBPReview.google_profile_id == GoogleBusinessProfile.id)
            .where(
                GoogleBusinessProfile.organization_id == org_id,
                GBPReview.reply_text.is_(None),
            )
        ) or 0

        last_audit_at = await db.scalar(
            select(AuditReport.completed_at)
            .where(
                AuditReport.organization_id == org_id,
                AuditReport.status == "completed",
            )
            .order_by(AuditReport.completed_at.desc())
            .limit(1)
        )

        summaries.append(
            AgencyDashboardClientSummary(
                client_org_id=org_id,
                client_org_name=client_org.name,
                plan=client_org.plan,
                location_count=location_count,
                avg_visibility_score=round(float(avg_score), 1) if avg_score is not None else None,
                open_review_count=open_reviews,
                last_audit_at=last_audit_at,
            )
        )

    all_scores = [s.avg_visibility_score for s in summaries if s.avg_visibility_score is not None]
    overall_avg = round(sum(all_scores) / len(all_scores), 1) if all_scores else None

    return AgencyDashboardResponse(
        total_clients=len(summaries),
        total_locations=total_locations,
        avg_visibility_score=overall_avg,
        clients=summaries,
    )


# ── Shareable client reports ──────────────────────────────────────────────────

@router.post(
    "/reports/{report_id}/share",
    response_model=ShareableReportTokenResponse,
    dependencies=_AGENCY_DEP,
)
async def generate_share_token(
    report_id: UUID,
    context: OrganizationContext = Depends(get_current_organization_context),
    db: AsyncSession = Depends(get_db_session),
) -> ShareableReportTokenResponse:
    """Generate a shareable public link for an audit report."""
    from app.core.config import get_settings

    report = await db.scalar(
        select(AuditReport).where(
            AuditReport.id == report_id,
            AuditReport.organization_id == context.organization.id,
            AuditReport.status == "completed",
        )
    )
    if report is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Completed audit report not found.",
        )

    if not report.share_token:
        report.share_token = secrets.token_urlsafe(32)
        db.add(report)
        await db.commit()

    settings = get_settings()
    base_url = str(settings.api_base_url).rstrip("/") if hasattr(settings, "api_base_url") else ""
    share_url = f"{base_url}/api/v1/agency/reports/public/{report.share_token}"

    return ShareableReportTokenResponse(
        report_id=report.id,
        share_token=report.share_token,
        share_url=share_url,
    )


@router.get("/reports/public/{token}", response_model=ShareableReportResponse)
async def view_shared_report(
    token: str,
    db: AsyncSession = Depends(get_db_session),
) -> ShareableReportResponse:
    """Return a public read-only audit report view (no authentication required)."""
    report = await db.scalar(
        select(AuditReport).where(AuditReport.share_token == token)
    )
    if report is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found.")

    profile = await db.get(GoogleBusinessProfile, report.google_profile_id)
    profile_name = profile.google_location_name if profile else "Unknown"

    branding = await db.scalar(
        select(AgencyBranding).where(AgencyBranding.organization_id == report.organization_id)
    )

    return ShareableReportResponse(
        report_id=report.id,
        profile_name=profile_name,
        visibility_score=report.visibility_score,
        completeness_score=report.completeness_score,
        review_score=report.review_score,
        engagement_score=report.engagement_score,
        recommendations=report.recommendations,
        completed_at=report.completed_at,
        branding=AgencyBrandingResponse.model_validate(branding) if branding else None,
    )


# ── Helpers ───────────────────────────────────────────────────────────────────

async def _get_or_create_branding(db: AsyncSession, org_id: UUID) -> AgencyBranding:
    branding = await db.scalar(
        select(AgencyBranding).where(AgencyBranding.organization_id == org_id)
    )
    if branding is None:
        branding = AgencyBranding(organization_id=org_id)
        db.add(branding)
        await db.commit()
        await db.refresh(branding)
    return branding
