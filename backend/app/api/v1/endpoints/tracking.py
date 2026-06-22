"""Tracking endpoints for queueing and polling background jobs."""

from __future__ import annotations

import logging
from uuid import UUID

from celery.result import AsyncResult
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db_session
from app.models.user import User
from app.rank_tracking.service import (
    create_heatmap_run,
    get_keyword_history,
    get_owned_heatmap_or_none,
    get_owned_keyword_or_none,
    get_owned_location_or_none,
    get_rank_tracking_overview,
    get_recent_heatmap_runs,
    serialize_heatmap_run,
)
from app.schemas.ranking import (
    HeatmapCreateRequest,
    HeatmapRunResponse,
    HeatmapTaskAcceptedResponse,
    ManualTriggerResponse,
    RankTrackingOverviewResponse,
    RankingHistoryResponse,
    TaskStatusResponse,
)
from app.schemas.task import TaskAcceptedResponse, TrackTestRequest
from app.worker.celery_app import celery_app
from app.worker.heatmap_tasks import generate_heatmap
from app.worker.tasks import fetch_serp_data, simulate_serp_scrape


logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/test",
    response_model=TaskAcceptedResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def enqueue_test_tracking_task(payload: TrackTestRequest) -> TaskAcceptedResponse:
    """Queue a non-blocking mock scrape job for a keyword."""
    logger.info("Queueing simulate_serp_scrape for keyword_id=%s", payload.keyword_id)

    try:
        task = simulate_serp_scrape.delay(str(payload.keyword_id))
    except Exception as exc:  # pragma: no cover - defensive transport handling
        logger.exception("Unable to queue simulated scrape for keyword_id=%s", payload.keyword_id)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Background worker is currently unavailable.",
        ) from exc

    return TaskAcceptedResponse(task_id=task.id, status="queued")


@router.get(
    "/test/{task_id}",
    response_model=TaskStatusResponse,
)
async def get_test_tracking_task_status(task_id: str) -> TaskStatusResponse:
    """Return the current Celery task state and result when available."""
    try:
        task_result = AsyncResult(task_id, app=celery_app)
    except Exception as exc:  # pragma: no cover - defensive backend handling
        logger.exception("Unable to load task status for task_id=%s", task_id)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Task backend is currently unavailable.",
        ) from exc

    state = task_result.state.lower()

    if state == "failure":
        logger.error("Task failed for task_id=%s: %s", task_id, task_result.result)
        return TaskStatusResponse(
            task_id=task_id,
            status=state,
            error=str(task_result.result),
        )

    if state == "success":
        result = task_result.result
        if not isinstance(result, dict):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Task completed with an unexpected response type.",
            )

        return TaskStatusResponse(
            task_id=task_id,
            status=state,
            result=result,
        )

    return TaskStatusResponse(task_id=task_id, status=state)


@router.get("/overview", response_model=RankTrackingOverviewResponse)
async def get_rank_tracking_dashboard(
    current_user: User = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session),
) -> RankTrackingOverviewResponse:
    """Return aggregate keyword tracking metrics for the authenticated user."""
    return await get_rank_tracking_overview(db_session, current_user)


@router.post(
    "/keywords/{keyword_id}/trigger",
    response_model=ManualTriggerResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def trigger_keyword_refresh(
    keyword_id: UUID,
    current_user: User = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session),
) -> ManualTriggerResponse:
    """Queue a live ranking refresh for one owned keyword."""
    keyword = await get_owned_keyword_or_none(db_session, current_user, keyword_id)
    if keyword is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Keyword was not found.")

    try:
        task = fetch_serp_data.delay(str(keyword.id))
    except Exception as exc:  # pragma: no cover - defensive broker handling
        logger.exception("Unable to queue live ranking refresh for keyword_id=%s", keyword_id)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Background worker is currently unavailable.",
        ) from exc

    return ManualTriggerResponse(task_id=task.id, keyword_id=keyword.id, status="queued")


@router.get("/keywords/{keyword_id}/history", response_model=RankingHistoryResponse)
async def get_owned_keyword_history(
    keyword_id: UUID,
    limit: int = Query(default=30, ge=1, le=180),
    current_user: User = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session),
) -> RankingHistoryResponse:
    """Return historical keyword rankings for one owned keyword."""
    keyword = await get_owned_keyword_or_none(db_session, current_user, keyword_id)
    if keyword is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Keyword was not found.")
    return await get_keyword_history(db_session, keyword, limit=limit)


@router.post(
    "/projects/{project_id}/heatmaps",
    response_model=HeatmapTaskAcceptedResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def queue_heatmap_generation(
    project_id: UUID,
    payload: HeatmapCreateRequest,
    current_user: User = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session),
) -> HeatmapTaskAcceptedResponse:
    """Queue a persisted heatmap generation run for one owned project."""
    location = await get_owned_location_or_none(db_session, current_user, payload.target_location_id)
    if location is None or location.project_id != project_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target location was not found.")

    if location.latitude is None or location.longitude is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Heatmaps require latitude and longitude on the target location.",
        )

    if payload.grid_size not in {5, 7, 9}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Heatmap grid_size must be one of 5, 7, or 9.",
        )

    keyword = None
    if payload.keyword_id is not None:
        keyword = await get_owned_keyword_or_none(db_session, current_user, payload.keyword_id)
        if keyword is None or keyword.project_id != project_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Keyword was not found.")

    heatmap_run = await create_heatmap_run(db_session, keyword, location, payload)

    try:
        task = generate_heatmap.delay(str(heatmap_run.id))
    except Exception as exc:  # pragma: no cover - defensive broker handling
        logger.exception("Unable to queue heatmap generation for heatmap_run_id=%s", heatmap_run.id)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Background worker is currently unavailable.",
        ) from exc

    return HeatmapTaskAcceptedResponse(task_id=task.id, heatmap_run_id=heatmap_run.id, status="queued")


@router.get("/heatmaps/recent", response_model=list[HeatmapRunResponse])
async def list_recent_heatmap_runs(
    current_user: User = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session),
) -> list[HeatmapRunResponse]:
    """Return recent heatmap runs across the authenticated user's projects."""
    return await get_recent_heatmap_runs(db_session, current_user)


@router.get("/heatmaps/{heatmap_run_id}", response_model=HeatmapRunResponse)
async def get_heatmap_run(
    heatmap_run_id: UUID,
    current_user: User = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session),
) -> HeatmapRunResponse:
    """Return one owned heatmap run."""
    heatmap_run = await get_owned_heatmap_or_none(db_session, current_user, heatmap_run_id)
    if heatmap_run is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Heatmap run was not found.")
    return serialize_heatmap_run(heatmap_run)


@router.get("/heatmaps/tasks/{task_id}", response_model=TaskStatusResponse)
async def get_heatmap_task_status(task_id: str) -> TaskStatusResponse:
    """Return Celery task state for a queued heatmap generation run."""
    return await get_test_tracking_task_status(task_id)
