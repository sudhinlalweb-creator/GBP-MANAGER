"""Google Business Profile integration models for the re-baselined platform."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.audit import AuditReport


class GoogleAccount(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Connected Google account authorized through OAuth."""

    __tablename__ = "google_accounts"
    __table_args__ = (
        UniqueConstraint("organization_id", "google_email", name="uq_google_accounts_org_email"),
    )

    organization_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    google_email: Mapped[str] = mapped_column(String(320), nullable=False)
    refresh_token_encrypted: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    access_token_expires_at: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)


class GoogleBusinessProfile(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """One synced GBP entity attached to an organization-owned location."""

    __tablename__ = "google_business_profiles"
    __table_args__ = (
        UniqueConstraint("organization_id", "google_location_name", name="uq_gbp_org_location_name"),
    )

    organization_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    google_account_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("google_accounts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    location_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True, index=True)
    google_location_name: Mapped[str] = mapped_column(String(255), nullable=False)
    primary_category: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    website_url: Mapped[Optional[str]] = mapped_column(String(2048), nullable=True)
    store_code: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    phone_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    address_formatted: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    address_street: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    address_city: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    address_state: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    address_postal_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    address_country_code: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    maps_url: Mapped[Optional[str]] = mapped_column(String(2048), nullable=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_suspended: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_disconnected: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    review_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    average_rating: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    total_photos: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    completeness_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    raw_api_data: Mapped[Optional[dict]] = mapped_column(
        postgresql.JSONB(astext_type=Text()),
        nullable=True,
    )
    last_synced_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    sync_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    audit_reports: Mapped[list["AuditReport"]] = relationship(
        back_populates="google_profile",
        cascade="all, delete-orphan",
        order_by="AuditReport.created_at.desc()",
    )
