"""Agency white-label and client management schemas."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class AgencyBrandingUpdateRequest(BaseModel):
    agency_name: str | None = Field(default=None, max_length=255)
    logo_url: str | None = Field(default=None, max_length=2048)
    brand_color: str | None = Field(default=None, pattern=r"^#[0-9A-Fa-f]{6}$")
    custom_domain: str | None = Field(default=None, max_length=255)
    reply_from_email: str | None = Field(default=None, max_length=320)
    report_footer_text: str | None = Field(default=None, max_length=2000)
    hide_platform_branding: bool | None = None


class AgencyBrandingResponse(BaseModel):
    id: UUID
    organization_id: UUID
    agency_name: str | None
    logo_url: str | None
    brand_color: str | None
    custom_domain: str | None
    reply_from_email: str | None
    report_footer_text: str | None
    hide_platform_branding: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AddClientRequest(BaseModel):
    client_org_id: UUID


class ClientLinkResponse(BaseModel):
    id: UUID
    agency_org_id: UUID
    client_org_id: UUID
    client_org_name: str
    client_org_plan: str
    is_active: bool
    linked_at: datetime

    model_config = {"from_attributes": True}


class AgencyDashboardClientSummary(BaseModel):
    client_org_id: UUID
    client_org_name: str
    plan: str
    location_count: int
    avg_visibility_score: float | None
    open_review_count: int
    last_audit_at: datetime | None


class AgencyDashboardResponse(BaseModel):
    total_clients: int
    total_locations: int
    avg_visibility_score: float | None
    clients: list[AgencyDashboardClientSummary]


class ShareableReportTokenResponse(BaseModel):
    report_id: UUID
    share_token: str
    share_url: str


class ShareableReportResponse(BaseModel):
    report_id: UUID
    profile_name: str
    visibility_score: int | None
    completeness_score: int | None
    review_score: int | None
    engagement_score: int | None
    recommendations: list | None
    completed_at: datetime | None
    branding: AgencyBrandingResponse | None
