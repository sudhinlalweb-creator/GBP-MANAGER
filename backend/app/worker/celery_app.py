"""Celery application bootstrap for background SERP jobs."""

from celery import Celery

from app.core.config import get_settings
from app.core.logging import configure_logging


configure_logging()
settings = get_settings()

celery_app = Celery(
    "gbp_manager",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=[
        "app.worker.ai_tasks",
        "app.worker.google_tasks",
        "app.worker.heatmap_tasks",
        "app.worker.tasks",
    ],
)

celery_app.conf.update(
    task_default_queue=settings.celery_default_queue,
    task_track_started=True,
    result_expires=3600,
    accept_content=["json"],
    task_serializer="json",
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)
