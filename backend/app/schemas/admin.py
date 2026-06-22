"""Read-only admin panel schemas."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class AdminOverviewResponse(BaseModel):
    """Top-level KPI summary for the admin control center."""

    active_users: int
    organizations: int
    monthly_recurring_revenue: float
    incident_status: str


class AdminUserItem(BaseModel):
    """One user row in the admin panel."""

    id: UUID
    name: str | None
    email: str
    role: str
    organization: str | None
    status: str
    is_active: bool
    last_active_at: datetime


class AdminOrganizationItem(BaseModel):
    """One tenant record in the admin panel."""

    id: UUID
    name: str
    subscription_tier: str
    locations_count: int
    members_count: int
    status: str
    renewal_date: datetime | None


class AdminSubscriptionItem(BaseModel):
    """Aggregated subscription mix row."""

    tier: str
    tenants_count: int
    members_count: int
    estimated_monthly_revenue: float
    status: str


class AdminServiceHealthItem(BaseModel):
    """One service health card in the admin control center."""

    name: str
    status: str
    detail: str
    metric: str


class AdminQueueHealthItem(BaseModel):
    """One async queue status item."""

    queue_name: str
    waiting: int
    running: int
    failed_24h: int


class AdminSystemHealthResponse(BaseModel):
    """Service and queue health summary."""

    services: list[AdminServiceHealthItem]
    queues: list[AdminQueueHealthItem]


class AdminUserStatusUpdateRequest(BaseModel):
    """Payload for activating or suspending a user."""

    is_active: bool


class AdminOrganizationTierUpdateRequest(BaseModel):
    """Payload for changing an organization's subscription tier."""

    subscription_tier: str = Field(..., min_length=1, max_length=50)


class AdminDashboardResponse(BaseModel):
    """Full admin panel response payload."""

    overview: AdminOverviewResponse
    users: list[AdminUserItem]
    organizations: list[AdminOrganizationItem]
    subscriptions: list[AdminSubscriptionItem]
    system_health: AdminSystemHealthResponse
