"""Historical ranking snapshots for keyword tracking runs."""

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


class RankingHistory(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Snapshot of a tracking job, including parsed SERP outputs and failures."""

    __tablename__ = "ranking_history"

    keyword_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("keywords.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
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
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending")
    error_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    query_keyword: Mapped[str] = mapped_column(String(255), nullable=False)
    location_label: Mapped[str] = mapped_column(String(255), nullable=False)
    uule: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    latitude: Mapped[Optional[Decimal]] = mapped_column(Numeric(9, 6), nullable=True)
    longitude: Mapped[Optional[Decimal]] = mapped_column(Numeric(9, 6), nullable=True)
    organic_rank: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    map_pack_rank: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    organic_results: Mapped[Optional[list[dict[str, Any]]]] = mapped_column(JSONB, nullable=True)
    map_pack_results: Mapped[Optional[list[dict[str, Any]]]] = mapped_column(JSONB, nullable=True)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    keyword: Mapped["Keyword"] = relationship(back_populates="ranking_history")
    project: Mapped["Project"] = relationship(back_populates="ranking_history")
    target_location: Mapped["TargetLocation"] = relationship(back_populates="ranking_history")
