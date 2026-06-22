"""create agency tables

Revision ID: d5e6f7a8b9c0
Revises: c3d4e5f6a7b8
Create Date: 2026-06-22 14:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "d5e6f7a8b9c0"
down_revision = "c3d4e5f6a7b8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "agency_branding",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False, unique=True),
        sa.Column("agency_name", sa.String(255), nullable=True),
        sa.Column("logo_url", sa.String(2048), nullable=True),
        sa.Column("brand_color", sa.String(7), nullable=True),
        sa.Column("custom_domain", sa.String(255), nullable=True),
        sa.Column("reply_from_email", sa.String(320), nullable=True),
        sa.Column("report_footer_text", sa.Text(), nullable=True),
        sa.Column("hide_platform_branding", sa.Boolean(), nullable=False, server_default="false"),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_agency_branding_organization_id", "agency_branding", ["organization_id"])

    op.create_table(
        "agency_client_links",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("agency_org_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("client_org_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["agency_org_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["client_org_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("agency_org_id", "client_org_id", name="uq_agency_client_links"),
    )
    op.create_index("ix_agency_client_links_agency_org_id", "agency_client_links", ["agency_org_id"])
    op.create_index("ix_agency_client_links_client_org_id", "agency_client_links", ["client_org_id"])

    # Add shareable report token column to audit_reports
    op.add_column(
        "audit_reports",
        sa.Column("share_token", sa.String(128), nullable=True, unique=True),
    )
    op.create_index("ix_audit_reports_share_token", "audit_reports", ["share_token"])


def downgrade() -> None:
    op.drop_index("ix_audit_reports_share_token", table_name="audit_reports")
    op.drop_column("audit_reports", "share_token")
    op.drop_index("ix_agency_client_links_client_org_id", table_name="agency_client_links")
    op.drop_index("ix_agency_client_links_agency_org_id", table_name="agency_client_links")
    op.drop_table("agency_client_links")
    op.drop_index("ix_agency_branding_organization_id", table_name="agency_branding")
    op.drop_table("agency_branding")
