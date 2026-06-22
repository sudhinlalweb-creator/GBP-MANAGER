"""Schemas for task queueing and task status responses."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class TrackTestRequest(BaseModel):
    """Input payload for the test tracking endpoint."""

    keyword_id: UUID = Field(..., description="Keyword identifier to simulate tracking for.")


class TaskAcceptedResponse(BaseModel):
    """Response returned after enqueuing a Celery task."""

    task_id: str
    status: str


class TaskStatusResponse(BaseModel):
    """Response returned when polling a Celery task."""

    task_id: str
    status: str
    result: dict[str, Any] | None = None
    error: str | None = None
