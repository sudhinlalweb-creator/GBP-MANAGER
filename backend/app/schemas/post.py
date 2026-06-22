"""Post schemas for GBP local post management endpoints."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class PostCreateRequest(BaseModel):
    summary: str = Field(..., min_length=1, max_length=1500)
    post_type: str = Field(default="STANDARD", pattern="^(STANDARD|EVENT|OFFER|ALERT)$")
    call_to_action_type: str | None = Field(default=None)
    call_to_action_url: str | None = Field(default=None, max_length=2048)
    media_url: str | None = Field(default=None, max_length=2048)
    scheduled_at: datetime | None = None


class PostResponse(BaseModel):
    id: UUID
    google_profile_id: UUID
    google_post_id: str | None
    post_type: str
    summary: str
    call_to_action_type: str | None
    call_to_action_url: str | None
    media_url: str | None
    state: str
    scheduled_at: datetime | None
    published_at: datetime | None
    error_reason: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PostListResponse(BaseModel):
    posts: list[PostResponse]
    total: int
