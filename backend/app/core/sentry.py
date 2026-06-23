"""Sentry initialisation helper.

Called once at process startup from both main.py (API) and celery_app.py (worker).
Is a no-op when SENTRY_DSN is not set, so local development is unaffected.

Sign up at sentry.io, create a Python project, and set:
    SENTRY_DSN=https://xxxx@oXXXX.ingest.sentry.io/YYYY
"""

from __future__ import annotations

import logging

import sentry_sdk
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration

from app.core.config import get_settings

logger = logging.getLogger(__name__)


def init_sentry() -> None:
    """Initialise Sentry SDK. Safe to call multiple times — SDK guards re-init."""
    settings = get_settings()

    if not settings.sentry_dsn:
        logger.debug("SENTRY_DSN not set — error tracking disabled.")
        return

    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        environment=settings.environment,
        # Capture 100 % of errors; sample 10 % of transactions for performance data.
        # Raise traces_sample_rate toward 1.0 only after confirming quota fits your plan.
        traces_sample_rate=0.1,
        send_default_pii=False,  # Never send passwords, tokens, or raw request bodies
        integrations=[
            StarletteIntegration(transaction_style="url"),
            FastApiIntegration(transaction_style="url"),
            CeleryIntegration(
                monitor_beat_tasks=True,  # alerts if a beat job stops firing
                propagate_traces=True,
            ),
            SqlalchemyIntegration(),
            LoggingIntegration(
                level=logging.INFO,       # capture INFO+ as breadcrumbs
                event_level=logging.ERROR,  # send ERROR+ as Sentry events
            ),
        ],
    )
    logger.info("Sentry initialised — environment=%s", settings.environment)
