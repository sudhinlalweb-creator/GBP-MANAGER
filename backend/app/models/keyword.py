"""Keyword model for project/location scoped SERP tracking terms."""

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    Boolean,
    ForeignKey,
    ForeignKeyConstraint,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.heatmap_run import HeatmapRun
    from app.models.project import Project
    from app.models.ranking_history import RankingHistory
    from app.models.target_location import TargetLocation


class Keyword(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Search term scoped to a project and a specific target location."""

    __tablename__ = "keywords"
    __table_args__ = (
        UniqueConstraint(
            "project_id",
            "target_location_id",
            "phrase",
            name="uq_keywords_project_location_phrase",
        ),
        ForeignKeyConstraint(
            ["target_location_id", "project_id"],
            ["target_locations.id", "target_locations.project_id"],
            ondelete="CASCADE",
            name="fk_keywords_target_location_project_scope",
        ),
    )

    project_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    target_location_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        nullable=False,
        index=True,
    )
    phrase: Mapped[str] = mapped_column(String(255), nullable=False)
    tracking_frequency_minutes: Mapped[int] = mapped_column(
        Integer,
        default=1440,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    project: Mapped["Project"] = relationship(back_populates="keywords")
    target_location: Mapped["TargetLocation"] = relationship(back_populates="keywords")
    ranking_history: Mapped[list["RankingHistory"]] = relationship(
        back_populates="keyword",
        cascade="all, delete-orphan",
    )
    heatmap_runs: Mapped[list["HeatmapRun"]] = relationship(back_populates="keyword")
