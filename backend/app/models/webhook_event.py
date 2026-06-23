"""Processed Stripe webhook event log for idempotency."""

from __future__ import annotations

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ProcessedWebhookEvent(Base):
    """Records every Stripe event ID that has been successfully processed.

    The UNIQUE constraint on event_id is the idempotency mechanism —
    a duplicate INSERT raises IntegrityError, which the handler catches
    and converts to an early-200 return without re-processing the event.
    """

    __tablename__ = "processed_webhook_events"

    event_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    event_type: Mapped[str] = mapped_column(String(128), nullable=False)
    processed_at: Mapped[object] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
