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


class TokenResponse(BaseModel):
    """JWT authentication response."""

    access_token: str
    token_type: str = "bearer"
    user: UserResponse
