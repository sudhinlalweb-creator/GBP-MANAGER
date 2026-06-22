"""Ranking history and heatmap schemas for rank tracking endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel


class ManualTriggerResponse(BaseModel):
    """Response returned after queueing a keyword refresh."""

    task_id: str
    keyword_id: UUID
    status: str


class RankingHistoryPoint(BaseModel):
    """One point in a keyword ranking history series."""

    ranking_history_id: UUID
    captured_at: datetime
    status: str
    organic_rank: int | None
    map_pack_rank: int | None
    error_reason: str | None


class RankingHistoryResponse(BaseModel):
    """Historical chart response for one keyword."""

    keyword_id: UUID
    project_id: UUID
    points: list[RankingHistoryPoint]


class KeywordTrendSummary(BaseModel):
    """Latest trend summary for one tracked keyword."""

    keyword_id: UUID
    project_id: UUID
    phrase: str
    latest_organic_rank: int | None
    previous_organic_rank: int | None
    latest_map_pack_rank: int | None
    trend_direction: str
    successful_runs: int
    failed_runs: int
    last_captured_at: datetime | None


class RankTrackingOverviewResponse(BaseModel):
    """Aggregate ranking metrics for the authenticated user's workspace."""

    projects_count: int
    tracked_locations: int
    active_keywords: int
    successful_runs_30d: int
    failed_runs_30d: int
    average_organic_rank: float | None
    average_map_pack_rank: float | None
    visibility_score: float
    keyword_trends: list[KeywordTrendSummary]


class TaskStatusResponse(BaseModel):
    """Task status response used by protected endpoints."""

    task_id: str
    status: str
    result: dict[str, Any] | None = None
    error: str | None = None


class HeatmapCreateRequest(BaseModel):
    """Payload used to enqueue a heatmap generation run."""

    target_location_id: UUID
    keyword_id: UUID | None = None
    grid_size: int = 5
    radius_meters: int = 750


class HeatmapPoint(BaseModel):
    """One point in a ranking heatmap grid."""

    latitude: float
    longitude: float
    organic_rank: int | None
    map_pack_rank: int | None
    grid_row: int
    grid_col: int


class HeatmapRunResponse(BaseModel):
    """Persisted heatmap run response."""

    id: UUID
    project_id: UUID
    target_location_id: UUID
    keyword_id: UUID | None
    project_name: str | None = None
    location_label: str | None = None
    keyword_phrase: str | None = None
    status: str
    error_reason: str | None
    grid_size: int
    radius_meters: int
    grid_points_total: int
    center_latitude: float
    center_longitude: float
    points: list[HeatmapPoint] = []
    summary: dict[str, Any] | None = None
    started_at: datetime
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime


class HeatmapTaskAcceptedResponse(BaseModel):
    """Response returned after queueing a heatmap generation task."""

    task_id: str
    heatmap_run_id: UUID
    status: str
