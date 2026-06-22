"""Background tasks for persisted geo-grid heatmap generation."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.db.session import AsyncSessionLocal
from app.models.heatmap_run import HeatmapRun
from app.models.ranking_history import RankingHistory
from app.worker.celery_app import celery_app


logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="app.worker.heatmap_tasks.generate_heatmap")
def generate_heatmap(self: object, heatmap_run_id: str) -> dict[str, object]:
    """Generate a persisted heatmap grid for a queued run."""
    del self
    return asyncio.run(_generate_heatmap_async(heatmap_run_id))


async def _generate_heatmap_async(heatmap_run_id: str) -> dict[str, object]:
    """Materialize one geo-grid run with deterministic scaffolded ranking values."""
    async with AsyncSessionLocal() as session:
        heatmap_run = await session.get(
            HeatmapRun,
            heatmap_run_id,
            options=(
                joinedload(HeatmapRun.keyword),
                joinedload(HeatmapRun.target_location),
            ),
        )
        if heatmap_run is None:
            raise ValueError(f"Heatmap run '{heatmap_run_id}' was not found.")

        heatmap_run.status = "running"
        heatmap_run.started_at = datetime.now(timezone.utc)
        session.add(heatmap_run)
        await session.commit()

        try:
            latest_history = await _get_latest_ranking_history(session, heatmap_run)
            points = _build_heatmap_points(
                center_latitude=float(heatmap_run.center_latitude),
                center_longitude=float(heatmap_run.center_longitude),
                grid_size=heatmap_run.grid_size,
                radius_meters=heatmap_run.radius_meters,
                seed_rank=latest_history.organic_rank if latest_history else 8,
                seed_map_pack_rank=latest_history.map_pack_rank if latest_history else 4,
            )
            heatmap_run.points = points
            heatmap_run.summary = _build_heatmap_summary(points)
            heatmap_run.status = "succeeded"
            heatmap_run.error_reason = None
            heatmap_run.completed_at = datetime.now(timezone.utc)
            session.add(heatmap_run)
            await session.commit()
        except Exception as exc:
            logger.exception("Heatmap generation failed for heatmap_run_id=%s", heatmap_run_id)
            await session.rollback()
            await _mark_heatmap_failed(session, heatmap_run_id, str(exc))
            raise

    return {
        "heatmap_run_id": heatmap_run_id,
        "status": "succeeded",
        "grid_points_total": heatmap_run.grid_points_total,
    }


async def _get_latest_ranking_history(
    session: AsyncSession,
    heatmap_run: HeatmapRun,
) -> RankingHistory | None:
    if heatmap_run.keyword_id is None:
        return None

    return await session.scalar(
        select(RankingHistory).where(
            RankingHistory.keyword_id == heatmap_run.keyword_id,
            RankingHistory.status == "succeeded",
        )
        .order_by(RankingHistory.completed_at.desc().nullslast(), RankingHistory.started_at.desc())
        .limit(1)
    )


def _build_heatmap_points(
    center_latitude: float,
    center_longitude: float,
    grid_size: int,
    radius_meters: int,
    seed_rank: int | None,
    seed_map_pack_rank: int | None,
) -> list[dict[str, int | float | None]]:
    step_degrees = radius_meters / 111_320
    center_index = grid_size // 2
    base_organic = max(1, seed_rank or 8)
    base_map_pack = max(1, seed_map_pack_rank or 4)

    points: list[dict[str, int | float | None]] = []
    for row in range(grid_size):
        for col in range(grid_size):
            lat_offset = (center_index - row) * step_degrees
            lng_offset = (col - center_index) * step_degrees
            distance_penalty = abs(center_index - row) + abs(center_index - col)
            organic_rank = min(20, base_organic + distance_penalty)
            map_pack_rank = min(10, base_map_pack + max(0, distance_penalty - 1))
            points.append(
                {
                    "latitude": round(center_latitude + lat_offset, 6),
                    "longitude": round(center_longitude + lng_offset, 6),
                    "organic_rank": organic_rank,
                    "map_pack_rank": map_pack_rank,
                    "grid_row": row,
                    "grid_col": col,
                }
            )
    return points


def _build_heatmap_summary(points: list[dict[str, int | float | None]]) -> dict[str, object]:
    organic_ranks = [point["organic_rank"] for point in points if point["organic_rank"] is not None]
    map_pack_ranks = [point["map_pack_rank"] for point in points if point["map_pack_rank"] is not None]
    return {
        "grid_points_completed": len(points),
        "best_organic_rank": min(organic_ranks) if organic_ranks else None,
        "best_map_pack_rank": min(map_pack_ranks) if map_pack_ranks else None,
        "average_organic_rank": round(sum(organic_ranks) / len(organic_ranks), 2) if organic_ranks else None,
        "average_map_pack_rank": round(sum(map_pack_ranks) / len(map_pack_ranks), 2)
        if map_pack_ranks
        else None,
    }


async def _mark_heatmap_failed(session: AsyncSession, heatmap_run_id: str, error_reason: str) -> None:
    heatmap_run = await session.get(HeatmapRun, heatmap_run_id)
    if heatmap_run is None:
        return

    heatmap_run.status = "failed"
    heatmap_run.error_reason = error_reason
    heatmap_run.completed_at = datetime.now(timezone.utc)
    session.add(heatmap_run)
    await session.commit()
