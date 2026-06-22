"""Target location schemas."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class LocationCreateRequest(BaseModel):
    """Payload used to create a location within a project."""

    label: str = Field(..., min_length=1, max_length=255)
    uule: str | None = Field(default=None, max_length=512)
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    city: str | None = Field(default=None, max_length=255)
    postal_code: str | None = Field(default=None, max_length=20)
    country_code: str | None = Field(default=None, min_length=2, max_length=2)


class LocationUpdateRequest(BaseModel):
    """Payload used to update a location."""

    label: str | None = Field(default=None, min_length=1, max_length=255)
    uule: str | None = Field(default=None, max_length=512)
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    city: str | None = Field(default=None, max_length=255)
    postal_code: str | None = Field(default=None, max_length=20)
    country_code: str | None = Field(default=None, min_length=2, max_length=2)


class LocationResponse(BaseModel):
    """Target location response payload."""

    id: UUID
    project_id: UUID
    label: str
    uule: str | None
    latitude: Decimal | None
    longitude: Decimal | None
    city: str | None
    postal_code: str | None
    country_code: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
