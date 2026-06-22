"""Celery application bootstrap for background SERP jobs."""

from celery import Celery
from celery.schedules import crontab

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
        "app.worker.post_tasks",
        "app.worker.review_tasks",
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

celery_app.conf.beat_schedule = {
    "nightly-gbp-sync": {
        "task": "app.worker.google_tasks.nightly_sync_all_accounts",
        "schedule": crontab(hour=3, minute=0),
    },
    "nightly-keyword-tracking": {
        "task": "app.worker.tasks.nightly_track_all_keywords",
        "schedule": crontab(hour=4, minute=0),
    },
    "nightly-review-sync": {
        "task": "app.worker.review_tasks.nightly_sync_all_reviews",
        "schedule": crontab(hour=5, minute=0),
    },
    "hourly-scheduled-posts": {
        "task": "app.worker.post_tasks.publish_scheduled_posts",
        "schedule": crontab(minute=0),
    },
}
