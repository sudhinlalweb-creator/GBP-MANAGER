"""Review schemas for GBP review management endpoints."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ReviewResponse(BaseModel):
    id: UUID
    google_profile_id: UUID
    google_review_id: str
    author_name: str | None
    author_photo_url: str | None
    rating: int | None
    comment: str | None
    review_time: datetime | None
    reply_text: str | None
    replied_at: datetime | None
    sentiment: str | None
    is_flagged: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ReviewListResponse(BaseModel):
    reviews: list[ReviewResponse]
    total: int


class ReviewReplyRequest(BaseModel):
    reply_text: str = Field(..., min_length=1, max_length=4096)


class ReviewReplyResponse(BaseModel):
    review_id: UUID
    reply_text: str
    replied_at: datetime


class ReviewSyncAcceptedResponse(BaseModel):
    message: str
    task_id: str
