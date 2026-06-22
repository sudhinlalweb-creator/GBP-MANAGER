"""create reviews posts automation tables

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-06-22 12:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "c3d4e5f6a7b8"
down_revision = "b2c3d4e5f6a7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "gbp_reviews",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("google_profile_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("google_review_id", sa.String(255), nullable=False),
        sa.Column("author_name", sa.String(255), nullable=True),
        sa.Column("author_photo_url", sa.String(2048), nullable=True),
        sa.Column("rating", sa.Integer(), nullable=True),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("review_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reply_text", sa.Text(), nullable=True),
        sa.Column("replied_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("sentiment", sa.String(20), nullable=True),
        sa.Column("is_flagged", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("raw_data", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["google_profile_id"], ["google_business_profiles.id"], ondelete="CASCADE"
        ),
        sa.UniqueConstraint("google_profile_id", "google_review_id", name="uq_gbp_reviews_profile_review"),
    )
    op.create_index("ix_gbp_reviews_google_profile_id", "gbp_reviews", ["google_profile_id"])

    op.create_table(
        "gbp_posts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("google_profile_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("google_post_id", sa.String(255), nullable=True),
        sa.Column("post_type", sa.String(50), nullable=False, server_default="STANDARD"),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("call_to_action_type", sa.String(50), nullable=True),
        sa.Column("call_to_action_url", sa.String(2048), nullable=True),
        sa.Column("media_url", sa.String(2048), nullable=True),
        sa.Column("state", sa.String(30), nullable=False, server_default="pending"),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_reason", sa.Text(), nullable=True),
        sa.Column("raw_data", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["google_profile_id"], ["google_business_profiles.id"], ondelete="CASCADE"
        ),
        sa.UniqueConstraint("google_profile_id", "google_post_id", name="uq_gbp_posts_profile_post"),
    )
    op.create_index("ix_gbp_posts_google_profile_id", "gbp_posts", ["google_profile_id"])

    op.create_table(
        "automation_rules",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("rule_type", sa.String(50), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("config", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_automation_rules_organization_id", "automation_rules", ["organization_id"])


def downgrade() -> None:
    op.drop_index("ix_automation_rules_organization_id", table_name="automation_rules")
    op.drop_table("automation_rules")
    op.drop_index("ix_gbp_posts_google_profile_id", table_name="gbp_posts")
    op.drop_table("gbp_posts")
    op.drop_index("ix_gbp_reviews_google_profile_id", table_name="gbp_reviews")
    op.drop_table("gbp_reviews")
