"""Target location model for geo-specific SERP tracking."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.heatmap_run import HeatmapRun
    from app.models.keyword import Keyword
    from app.models.project import Project
    from app.models.ranking_history import RankingHistory


class TargetLocation(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Geographic target within a project."""

    __tablename__ = "target_locations"
    __table_args__ = (
        UniqueConstraint("id", "project_id", name="uq_target_locations_id_project_id"),
        UniqueConstraint(
            "project_id",
            "uule",
            name="uq_target_locations_project_uule",
        ),
    )

    project_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    uule: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    latitude: Mapped[Optional[Decimal]] = mapped_column(Numeric(9, 6), nullable=True)
    longitude: Mapped[Optional[Decimal]] = mapped_column(Numeric(9, 6), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    postal_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    country_code: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)

    project: Mapped["Project"] = relationship(back_populates="target_locations")
    keywords: Mapped[list["Keyword"]] = relationship(
        back_populates="target_location",
        cascade="all, delete-orphan",
    )
    ranking_history: Mapped[list["RankingHistory"]] = relationship(
        back_populates="target_location",
        cascade="all, delete-orphan",
    )
    heatmap_runs: Mapped[list["HeatmapRun"]] = relationship(
        back_populates="target_location",
        cascade="all, delete-orphan",
    )
