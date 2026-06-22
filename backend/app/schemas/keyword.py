"""Keyword schemas."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class KeywordCreateRequest(BaseModel):
    """Payload used to create a keyword."""

    phrase: str = Field(..., min_length=1, max_length=255)
    target_location_id: UUID
    tracking_frequency_minutes: int = Field(default=1440, ge=5, le=10080)
    is_active: bool = True


class KeywordUpdateRequest(BaseModel):
    """Payload used to update a keyword."""

    phrase: str | None = Field(default=None, min_length=1, max_length=255)
    target_location_id: UUID | None = None
    tracking_frequency_minutes: int | None = Field(default=None, ge=5, le=10080)
    is_active: bool | None = None


class KeywordResponse(BaseModel):
    """Keyword response payload."""

    id: UUID
    project_id: UUID
    target_location_id: UUID
    phrase: str
    tracking_frequency_minutes: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
