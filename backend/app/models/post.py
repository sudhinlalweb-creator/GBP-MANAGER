"""Google Business Profile local post model."""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.google.models import GoogleBusinessProfile


class GBPPost(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A local post created on a Google Business Profile."""

    __tablename__ = "gbp_posts"
    __table_args__ = (
        UniqueConstraint("google_profile_id", "google_post_id", name="uq_gbp_posts_profile_post"),
    )

    google_profile_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("google_business_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    google_post_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    post_type: Mapped[str] = mapped_column(String(50), nullable=False, default="STANDARD")
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    call_to_action_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    call_to_action_url: Mapped[Optional[str]] = mapped_column(String(2048), nullable=True)
    media_url: Mapped[Optional[str]] = mapped_column(String(2048), nullable=True)
    # pending | scheduled | published | failed | deleted
    state: Mapped[str] = mapped_column(String(30), nullable=False, default="pending")
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    error_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    raw_data: Mapped[Optional[dict]] = mapped_column(
        __import__("sqlalchemy.dialects.postgresql", fromlist=["JSONB"]).JSONB(astext_type=Text()),
        nullable=True,
    )

    google_profile: Mapped["GoogleBusinessProfile"] = relationship(back_populates="posts")
