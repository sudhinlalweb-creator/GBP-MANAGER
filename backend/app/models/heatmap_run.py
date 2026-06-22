"""Persisted geo-grid heatmap runs for local ranking visibility analysis."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import TYPE_CHECKING, Any, Optional
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.keyword import Keyword
    from app.models.project import Project
    from app.models.target_location import TargetLocation


class HeatmapRun(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """One heatmap job and its persisted geo-grid ranking output."""

    __tablename__ = "heatmap_runs"

    project_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    target_location_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("target_locations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    keyword_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("keywords.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="queued")
    error_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    grid_size: Mapped[int] = mapped_column(Integer, nullable=False)
    radius_meters: Mapped[int] = mapped_column(Integer, nullable=False)
    grid_points_total: Mapped[int] = mapped_column(Integer, nullable=False)
    center_latitude: Mapped[Decimal] = mapped_column(Numeric(9, 6), nullable=False)
    center_longitude: Mapped[Decimal] = mapped_column(Numeric(9, 6), nullable=False)
    points: Mapped[Optional[list[dict[str, Any]]]] = mapped_column(JSONB, nullable=True)
    summary: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    project: Mapped["Project"] = relationship(back_populates="heatmap_runs")
    target_location: Mapped["TargetLocation"] = relationship(back_populates="heatmap_runs")
    keyword: Mapped[Optional["Keyword"]] = relationship(back_populates="heatmap_runs")
