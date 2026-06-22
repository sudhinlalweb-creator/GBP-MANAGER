"""create audit reports table

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-06-22 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "b2c3d4e5f6a7"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "audit_reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("google_profile_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("requested_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="pending"),
        sa.Column("visibility_score", sa.Integer(), nullable=True),
        sa.Column("completeness_score", sa.Integer(), nullable=True),
        sa.Column("review_score", sa.Integer(), nullable=True),
        sa.Column("engagement_score", sa.Integer(), nullable=True),
        sa.Column("ai_provider", sa.String(50), nullable=True),
        sa.Column("ai_model", sa.String(100), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_reason", sa.Text(), nullable=True),
        sa.Column("raw_ai_response", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("recommendations", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["google_profile_id"], ["google_business_profiles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["requested_by_user_id"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_audit_reports_organization_id", "audit_reports", ["organization_id"])
    op.create_index("ix_audit_reports_google_profile_id", "audit_reports", ["google_profile_id"])
    op.create_index("ix_audit_reports_requested_by_user_id", "audit_reports", ["requested_by_user_id"])


def downgrade() -> None:
    op.drop_index("ix_audit_reports_requested_by_user_id", table_name="audit_reports")
    op.drop_index("ix_audit_reports_google_profile_id", table_name="audit_reports")
    op.drop_index("ix_audit_reports_organization_id", table_name="audit_reports")
    op.drop_table("audit_reports")
