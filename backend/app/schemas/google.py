"""Schemas for Google Business Profile integration and dashboard responses."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class GoogleOAuthConnectResponse(BaseModel):
    """Response returned when building a Google OAuth authorization URL."""

    authorization_url: str
    state: str


class GoogleOAuthCallbackRequest(BaseModel):
    """Authorization code payload posted from the frontend after Google redirect."""

    code: str = Field(..., min_length=1)
    state: str = Field(..., min_length=1)


class GoogleAccountResponse(BaseModel):
    """Safe Google account payload exposed to the frontend."""

    id: UUID
    organization_id: UUID
    google_email: str
    access_token_expires_at: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class GoogleBusinessProfileResponse(BaseModel):
    """Safe Google Business Profile payload exposed to the frontend."""

    id: UUID
    organization_id: UUID
    google_account_id: UUID
    location_id: UUID | None
    google_location_name: str
    primary_category: str | None
    website_url: str | None
    store_code: str | None
    phone_number: str | None
    address_formatted: str | None
    address_street: str | None
    address_city: str | None
    address_state: str | None
    address_postal_code: str | None
    address_country_code: str | None
    latitude: float | None
    longitude: float | None
    maps_url: str | None
    is_verified: bool
    is_suspended: bool
    review_count: int | None
    average_rating: float | None
    total_photos: int | None
    completeness_score: int | None
    last_synced_at: datetime | None
    sync_error: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class GoogleSyncAcceptedResponse(BaseModel):
    """Response returned when a sync job is queued."""

    message: str
    task_id: str


class GoogleIntegrationStatusResponse(BaseModel):
    """Integration readiness for the authenticated organization."""

    organization_id: UUID
    organization_name: str
    organization_role: str
    google_oauth_configured: bool
    google_maps_configured: bool
    worker_configured: bool
    connected_accounts: int
    synced_profiles: int
    last_profile_sync_at: datetime | None


class GoogleDashboardResponse(BaseModel):
    """Dashboard summary used by the Phase 2 frontend route."""

    organization_id: UUID
    organization_name: str
    connected_accounts: int
    synced_profiles: int
    linked_locations: int
    last_profile_sync_at: datetime | None
    accounts: list[GoogleAccountResponse]
    profiles: list[GoogleBusinessProfileResponse]


class GoogleSyncResult(BaseModel):
    """Structured result returned from a Google account sync run."""

    organization_id: UUID
    google_account_id: UUID
    connected_email: str
    accounts_fetched: int
    profiles_synced: int
    raw_accounts: list[dict[str, Any]]


class ProfileListResponse(BaseModel):
    """Paginated organization-scoped Google Business Profile list."""

    profiles: list[GoogleBusinessProfileResponse]
    total: int
