"""Organization-first tenancy foundation models for the re-baselined platform."""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.automation import AutomationRule


class Organization(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Top-level tenant boundary for the Local SEO SaaS platform."""

    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    plan: Mapped[str] = mapped_column(String(50), default="trial", nullable=False)
    subscription_tier: Mapped[str] = mapped_column(String(50), default="trial", nullable=False)
    location_limit: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    keyword_limit: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    billing_email: Mapped[Optional[str]] = mapped_column(String(320), nullable=True)
    stripe_customer_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        unique=True,
        nullable=True,
        index=True,
    )
    stripe_subscription_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        unique=True,
        nullable=True,
        index=True,
    )
    stripe_price_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    subscription_status: Mapped[str] = mapped_column(
        String(50),
        default="trialing",
        nullable=False,
    )
    trial_ends_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    subscription_current_period_end: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    cancel_at_period_end: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    automation_rules: Mapped[list["AutomationRule"]] = relationship(
        back_populates="organization",
        cascade="all, delete-orphan",
    )


class OrganizationMembership(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Association between a user and an organization with an explicit role."""

    __tablename__ = "organization_memberships"
    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "user_id",
            name="uq_organization_memberships_organization_user",
        ),
    )

    organization_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    role: Mapped[str] = mapped_column(String(50), default="owner", nullable=False)
    invitation_email: Mapped[Optional[str]] = mapped_column(String(320), nullable=True)
    is_pending: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    invited_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
