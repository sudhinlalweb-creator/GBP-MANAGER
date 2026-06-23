"""Shared rate-limiter instance for SlowAPI.

Import `limiter` in main.py (to register with the app) and in any router
that needs per-endpoint limits. Never instantiate Limiter elsewhere.

Storage: Redis (same instance as Celery broker).
Falls back to in-memory if Redis is unreachable — fail open, not fail closed.
"""

from __future__ import annotations

from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import get_settings


def _make_limiter() -> Limiter:
    settings = get_settings()
    return Limiter(
        key_func=get_remote_address,
        storage_uri=settings.celery_broker_url,
        # Swallow storage errors so a Redis blip never blocks login
        swallow_errors=True,
    )


limiter: Limiter = _make_limiter()
