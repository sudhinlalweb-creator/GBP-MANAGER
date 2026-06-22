"""Authentication request and response schemas."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class UserRegisterRequest(BaseModel):
    """Payload used to register a new user."""

    email: str = Field(..., max_length=320)
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=255)


class UserLoginRequest(BaseModel):
    """Payload used to authenticate a user."""

    email: str = Field(..., max_length=320)
    password: str = Field(..., min_length=8, max_length=128)


class RefreshTokenRequest(BaseModel):
    """Payload used to exchange a refresh token for a new token pair."""

    refresh_token: str = Field(..., min_length=1)


class LogoutRequest(BaseModel):
    """Payload used to revoke a refresh token."""

    refresh_token: str = Field(..., min_length=1)


class ForgotPasswordRequest(BaseModel):
    """Payload used to request a password reset link."""

    email: str = Field(..., max_length=320)


class ResetPasswordRequest(BaseModel):
    """Payload used to apply a new password with a reset token."""

    token: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8, max_length=128)


class UpdateMeRequest(BaseModel):
    """Payload used to update the authenticated profile."""

    full_name: str | None = Field(default=None, max_length=255)


class MessageResponse(BaseModel):
    """Simple status message payload."""

    message: str


class OrganizationMembershipResponse(BaseModel):
    """Organization membership returned with the authenticated profile."""

    organization_id: UUID
    organization_name: str
    organization_slug: str
    subscription_tier: str
    role: str
    joined_at: datetime


class UserResponse(BaseModel):
    """Safe user profile response."""

    id: UUID
    email: str
    full_name: str | None
    subscription_status: str
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AuthenticatedUserResponse(UserResponse):
    """User profile enriched with organization memberships."""

    memberships: list[OrganizationMembershipResponse] = Field(default_factory=list)


class TokenResponse(BaseModel):
    """JWT authentication response."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: AuthenticatedUserResponse
