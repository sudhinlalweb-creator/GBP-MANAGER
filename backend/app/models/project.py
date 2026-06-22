"""Project model representing a tenant workspace container."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.heatmap_run import HeatmapRun
    from app.models.keyword import Keyword
    from app.models.ranking_history import RankingHistory
    from app.models.target_location import TargetLocation
    from app.models.user import User


class Project(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Top-level project owned by a single user."""

    __tablename__ = "projects"
    __table_args__ = (
        UniqueConstraint("owner_id", "slug", name="uq_projects_owner_slug"),
    )

    owner_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    owner: Mapped["User"] = relationship(back_populates="projects")
    target_locations: Mapped[list["TargetLocation"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )
    keywords: Mapped[list["Keyword"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )
    ranking_history: Mapped[list["RankingHistory"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )
    heatmap_runs: Mapped[list["HeatmapRun"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )
