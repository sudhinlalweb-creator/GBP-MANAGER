"""Service layer for keyword ranking history and heatmap orchestration."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.heatmap_run import HeatmapRun
from app.models.keyword import Keyword
from app.models.project import Project
from app.models.ranking_history import RankingHistory
from app.models.target_location import TargetLocation
from app.models.user import User
from app.schemas.ranking import (
    HeatmapCreateRequest,
    HeatmapPoint,
    HeatmapRunResponse,
    KeywordTrendSummary,
    RankTrackingOverviewResponse,
    RankingHistoryPoint,
    RankingHistoryResponse,
)


async def get_rank_tracking_overview(
    db_session: AsyncSession,
    current_user: User,
) -> RankTrackingOverviewResponse:
    """Return aggregate ranking metrics across the authenticated user's projects."""
    project_ids = await _get_owned_project_ids(db_session, current_user.id)
    if not project_ids:
        return RankTrackingOverviewResponse(
            projects_count=0,
            tracked_locations=0,
            active_keywords=0,
            successful_runs_30d=0,
            failed_runs_30d=0,
            average_organic_rank=None,
            average_map_pack_rank=None,
            visibility_score=0.0,
            keyword_trends=[],
        )

    now = datetime.now(timezone.utc)
    recent_window = now - timedelta(days=30)

    tracked_locations = await db_session.scalar(
        select(func.count(TargetLocation.id)).where(TargetLocation.project_id.in_(project_ids))
    )
    active_keywords = await db_session.scalar(
        select(func.count(Keyword.id)).where(
            Keyword.project_id.in_(project_ids),
            Keyword.is_active.is_(True),
        )
    )

    recent_histories = (
        await db_session.scalars(
            select(RankingHistory)
            .where(
                RankingHistory.project_id.in_(project_ids),
                RankingHistory.started_at >= recent_window,
            )
            .order_by(RankingHistory.completed_at.desc().nullslast(), RankingHistory.started_at.desc())
        )
    ).all()

    successful_runs = [history for history in recent_histories if history.status == "succeeded"]
    failed_runs = [history for history in recent_histories if history.status == "failed"]
    organic_ranks = [history.organic_rank for history in successful_runs if history.organic_rank is not None]
    map_pack_ranks = [
        history.map_pack_rank for history in successful_runs if history.map_pack_rank is not None
    ]

    keyword_rows = (
        await db_session.execute(
            select(Keyword, Project)
            .join(Project, Keyword.project_id == Project.id)
            .where(Project.owner_id == current_user.id)
            .order_by(Project.created_at.asc(), Keyword.created_at.asc())
        )
    ).all()

    histories_by_keyword: dict[UUID, list[RankingHistory]] = defaultdict(list)
    for history in recent_histories:
        histories_by_keyword[history.keyword_id].append(history)

    keyword_trends: list[KeywordTrendSummary] = []
    for keyword, _project in keyword_rows:
        histories = histories_by_keyword.get(keyword.id, [])
        latest = histories[0] if histories else None
        previous = histories[1] if len(histories) > 1 else None
        successful_count = sum(1 for history in histories if history.status == "succeeded")
        failed_count = sum(1 for history in histories if history.status == "failed")
        keyword_trends.append(
            KeywordTrendSummary(
                keyword_id=keyword.id,
                project_id=keyword.project_id,
                phrase=keyword.phrase,
                latest_organic_rank=latest.organic_rank if latest else None,
                previous_organic_rank=previous.organic_rank if previous else None,
                latest_map_pack_rank=latest.map_pack_rank if latest else None,
                trend_direction=_determine_trend_direction(
                    latest.organic_rank if latest else None,
                    previous.organic_rank if previous else None,
                ),
                successful_runs=successful_count,
                failed_runs=failed_count,
                last_captured_at=(latest.completed_at or latest.started_at) if latest else None,
            )
        )

    visibility_score = _calculate_visibility_score(organic_ranks)

    return RankTrackingOverviewResponse(
        projects_count=len(project_ids),
        tracked_locations=int(tracked_locations or 0),
        active_keywords=int(active_keywords or 0),
        successful_runs_30d=len(successful_runs),
        failed_runs_30d=len(failed_runs),
        average_organic_rank=_calculate_average(organic_ranks),
        average_map_pack_rank=_calculate_average(map_pack_ranks),
        visibility_score=visibility_score,
        keyword_trends=keyword_trends[:8],
    )


async def get_keyword_history(
    db_session: AsyncSession,
    keyword: Keyword,
    limit: int = 30,
) -> RankingHistoryResponse:
    """Return recent ranking history points for one keyword."""
    histories = (
        await db_session.scalars(
            select(RankingHistory)
            .where(RankingHistory.keyword_id == keyword.id)
            .order_by(RankingHistory.started_at.desc())
            .limit(limit)
        )
    ).all()

    points = [
        RankingHistoryPoint(
            ranking_history_id=history.id,
            captured_at=history.completed_at or history.started_at,
            status=history.status,
            organic_rank=history.organic_rank,
            map_pack_rank=history.map_pack_rank,
            error_reason=history.error_reason,
        )
        for history in reversed(histories)
    ]

    return RankingHistoryResponse(keyword_id=keyword.id, project_id=keyword.project_id, points=points)


async def create_heatmap_run(
    db_session: AsyncSession,
    keyword: Keyword | None,
    location: TargetLocation,
    payload: HeatmapCreateRequest,
) -> HeatmapRun:
    """Persist a queued heatmap run for later async processing."""
    grid_points_total = payload.grid_size * payload.grid_size
    heatmap_run = HeatmapRun(
        project_id=location.project_id,
        target_location_id=location.id,
        keyword_id=keyword.id if keyword else None,
        status="queued",
        grid_size=payload.grid_size,
        radius_meters=payload.radius_meters,
        grid_points_total=grid_points_total,
        center_latitude=location.latitude or Decimal("0"),
        center_longitude=location.longitude or Decimal("0"),
        points=[],
        summary={
            "grid_points_completed": 0,
            "best_organic_rank": None,
            "best_map_pack_rank": None,
        },
    )
    db_session.add(heatmap_run)
    await db_session.commit()
    await db_session.refresh(heatmap_run)
    return heatmap_run


async def get_recent_heatmap_runs(
    db_session: AsyncSession,
    current_user: User,
    limit: int = 6,
) -> list[HeatmapRunResponse]:
    """Return recent heatmap runs across the authenticated user's projects."""
    statement = (
        select(HeatmapRun)
        .join(Project, HeatmapRun.project_id == Project.id)
        .options(
            joinedload(HeatmapRun.project),
            joinedload(HeatmapRun.target_location),
            joinedload(HeatmapRun.keyword),
        )
        .where(Project.owner_id == current_user.id)
        .order_by(HeatmapRun.created_at.desc())
        .limit(limit)
    )
    heatmap_runs = (await db_session.scalars(statement)).unique().all()
    return [_serialize_heatmap_run(heatmap_run) for heatmap_run in heatmap_runs]


async def get_owned_keyword_or_none(
    db_session: AsyncSession,
    current_user: User,
    keyword_id: UUID,
) -> Keyword | None:
    """Return a keyword only when it belongs to one of the user's projects."""
    statement: Select[tuple[Keyword]] = (
        select(Keyword)
        .join(Project, Keyword.project_id == Project.id)
        .where(Keyword.id == keyword_id, Project.owner_id == current_user.id)
    )
    return await db_session.scalar(statement)


async def get_owned_location_or_none(
    db_session: AsyncSession,
    current_user: User,
    location_id: UUID,
) -> TargetLocation | None:
    """Return a location only when it belongs to one of the user's projects."""
    statement: Select[tuple[TargetLocation]] = (
        select(TargetLocation)
        .join(Project, TargetLocation.project_id == Project.id)
        .where(TargetLocation.id == location_id, Project.owner_id == current_user.id)
    )
    return await db_session.scalar(statement)


async def get_owned_heatmap_or_none(
    db_session: AsyncSession,
    current_user: User,
    heatmap_run_id: UUID,
) -> HeatmapRun | None:
    """Return one heatmap run only when it belongs to the authenticated user."""
    statement = (
        select(HeatmapRun)
        .join(Project, HeatmapRun.project_id == Project.id)
        .options(
            joinedload(HeatmapRun.project),
            joinedload(HeatmapRun.target_location),
            joinedload(HeatmapRun.keyword),
        )
        .where(HeatmapRun.id == heatmap_run_id, Project.owner_id == current_user.id)
    )
    return await db_session.scalar(statement)


def serialize_heatmap_run(heatmap_run: HeatmapRun) -> HeatmapRunResponse:
    """Public serializer for heatmap runs."""
    return _serialize_heatmap_run(heatmap_run)


async def _get_owned_project_ids(db_session: AsyncSession, user_id: UUID) -> list[UUID]:
    project_ids = (
        await db_session.scalars(select(Project.id).where(Project.owner_id == user_id).order_by(Project.created_at))
    ).all()
    return list(project_ids)


def _calculate_average(values: list[int]) -> float | None:
    if not values:
        return None
    return round(sum(values) / len(values), 2)


def _calculate_visibility_score(organic_ranks: list[int]) -> float:
    if not organic_ranks:
        return 0.0

    weighted = [max(0, 100 - ((rank - 1) * 5)) for rank in organic_ranks]
    return round(sum(weighted) / len(weighted), 1)


def _determine_trend_direction(latest_rank: int | None, previous_rank: int | None) -> str:
    if latest_rank is None or previous_rank is None:
        return "stable"
    if latest_rank < previous_rank:
        return "up"
    if latest_rank > previous_rank:
        return "down"
    return "stable"


def _serialize_heatmap_run(heatmap_run: HeatmapRun) -> HeatmapRunResponse:
    points = [
        HeatmapPoint(
            latitude=float(point["latitude"]),
            longitude=float(point["longitude"]),
            organic_rank=point.get("organic_rank"),
            map_pack_rank=point.get("map_pack_rank"),
            grid_row=point["grid_row"],
            grid_col=point["grid_col"],
        )
        for point in (heatmap_run.points or [])
    ]
    return HeatmapRunResponse(
        id=heatmap_run.id,
        project_id=heatmap_run.project_id,
        target_location_id=heatmap_run.target_location_id,
        keyword_id=heatmap_run.keyword_id,
        project_name=heatmap_run.project.name if heatmap_run.project else None,
        location_label=heatmap_run.target_location.label if heatmap_run.target_location else None,
        keyword_phrase=heatmap_run.keyword.phrase if heatmap_run.keyword else None,
        status=heatmap_run.status,
        error_reason=heatmap_run.error_reason,
        grid_size=heatmap_run.grid_size,
        radius_meters=heatmap_run.radius_meters,
        grid_points_total=heatmap_run.grid_points_total,
        center_latitude=float(heatmap_run.center_latitude),
        center_longitude=float(heatmap_run.center_longitude),
        points=points,
        summary=heatmap_run.summary,
        started_at=heatmap_run.started_at,
        completed_at=heatmap_run.completed_at,
        created_at=heatmap_run.created_at,
        updated_at=heatmap_run.updated_at,
    )
