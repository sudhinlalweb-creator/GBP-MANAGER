"""Audit report model for AI-generated GBP location audits."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.google.models import GoogleBusinessProfile
    from app.models.user import User
    from app.organizations.models import Organization


class AuditReport(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """AI-generated audit report for one GBP location."""

    __tablename__ = "audit_reports"

    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    google_profile_id: Mapped[UUID] = mapped_column(
        ForeignKey("google_business_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    requested_by_user_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)
    visibility_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    completeness_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    review_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    engagement_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    ai_provider: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    ai_model: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    error_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    raw_ai_response: Mapped[Optional[dict]] = mapped_column(
        JSONB(astext_type=Text()), nullable=True
    )
    recommendations: Mapped[Optional[list]] = mapped_column(
        JSONB(astext_type=Text()), nullable=True
    )

    google_profile: Mapped["GoogleBusinessProfile"] = relationship(back_populates="audit_reports")
    organization: Mapped["Organization"] = relationship()
    requested_by: Mapped[Optional["User"]] = relationship()
