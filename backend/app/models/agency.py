"""Agency white-label branding and client account link models."""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.organizations.models import Organization


class AgencyBranding(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """White-label branding settings for an agency org."""

    __tablename__ = "agency_branding"

    organization_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    agency_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    logo_url: Mapped[Optional[str]] = mapped_column(String(2048), nullable=True)
    brand_color: Mapped[Optional[str]] = mapped_column(String(7), nullable=True)  # hex e.g. #FF5733
    custom_domain: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    reply_from_email: Mapped[Optional[str]] = mapped_column(String(320), nullable=True)
    report_footer_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    hide_platform_branding: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    organization: Mapped["Organization"] = relationship(back_populates="agency_branding")


class AgencyClientLink(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Many-to-many link between an agency org and its managed client orgs."""

    __tablename__ = "agency_client_links"
    __table_args__ = (
        UniqueConstraint("agency_org_id", "client_org_id", name="uq_agency_client_links"),
    )

    agency_org_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    client_org_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    agency_org: Mapped["Organization"] = relationship(
        foreign_keys=[agency_org_id],
        back_populates="managed_clients",
    )
    client_org: Mapped["Organization"] = relationship(
        foreign_keys=[client_org_id],
        back_populates="managed_by_agencies",
    )
