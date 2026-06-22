"""Google Business Profile review model."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.google.models import GoogleBusinessProfile


class GBPReview(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A customer review synced from the Google Business Profile API."""

    __tablename__ = "gbp_reviews"
    __table_args__ = (
        UniqueConstraint("google_profile_id", "google_review_id", name="uq_gbp_reviews_profile_review"),
    )

    google_profile_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("google_business_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    google_review_id: Mapped[str] = mapped_column(String(255), nullable=False)
    author_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    author_photo_url: Mapped[Optional[str]] = mapped_column(String(2048), nullable=True)
    rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    review_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    reply_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    replied_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    sentiment: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # positive|neutral|negative
    is_flagged: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    raw_data: Mapped[Optional[dict]] = mapped_column(
        __import__("sqlalchemy.dialects.postgresql", fromlist=["JSONB"]).JSONB(astext_type=Text()),
        nullable=True,
    )

    google_profile: Mapped["GoogleBusinessProfile"] = relationship(back_populates="reviews")
