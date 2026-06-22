"""Google Business Profile integration models for the re-baselined platform."""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


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
