"""Organization and membership API schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class OrganizationResponse(BaseModel):
    """Serialized organization payload for a tenant membership."""

    id: UUID
    name: str
    slug: str
    plan: str
    subscription_tier: str
    subscription_status: str
    location_limit: int
    keyword_limit: int
    trial_ends_at: datetime | None
    created_at: datetime


class OrganizationUpdateRequest(BaseModel):
    """Editable organization fields."""

    name: str | None = Field(default=None, min_length=1, max_length=255)
    slug: str | None = Field(
        default=None,
        min_length=3,
        max_length=60,
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
    )


class MemberResponse(BaseModel):
    """One organization member or pending invite."""

    user_id: UUID | None
    email: str | None
    full_name: str | None
    role: str
    is_pending: bool
    joined_at: datetime


class InviteRequest(BaseModel):
    """Invite a member into an organization."""

    email: str = Field(..., min_length=3, max_length=320)
    role: Literal["admin", "manager", "viewer"]


class AcceptInviteRequest(BaseModel):
    """Accept an organization invite token."""

    token: str = Field(..., min_length=1)
