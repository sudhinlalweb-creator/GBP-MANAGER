"""Automation rule model for review auto-reply and scheduled post triggers."""

from __future__ import annotations

from typing import Any, Optional
from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.organizations.models import Organization


class AutomationRule(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """An org-scoped automation rule (auto-reply or scheduled posting)."""

    __tablename__ = "automation_rules"

    organization_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # auto_reply_positive | auto_reply_neutral | auto_reply_negative | scheduled_post
    rule_type: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    # JSON config: e.g. {"template": "...", "min_rating": 4} for auto-reply
    config: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True)

    organization: Mapped["Organization"] = relationship(back_populates="automation_rules")
