"""add organization plan limit fields

Revision ID: f0e1d2c3b4a5
Revises: d4c2a7d9f1b0
Create Date: 2026-06-22 00:00:02.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "f0e1d2c3b4a5"
down_revision = "d4c2a7d9f1b0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "organizations",
        sa.Column("plan", sa.String(length=50), server_default="trial", nullable=False),
    )
    op.add_column(
        "organizations",
        sa.Column("location_limit", sa.Integer(), server_default="1", nullable=False),
    )
    op.add_column(
        "organizations",
        sa.Column("keyword_limit", sa.Integer(), server_default="5", nullable=False),
    )

    op.execute(
        """
        UPDATE organizations
        SET
            plan = CASE
                WHEN subscription_tier IN ('starter', 'pro', 'agency', 'trial') THEN subscription_tier
                ELSE 'trial'
            END,
            location_limit = CASE
                WHEN subscription_tier = 'starter' THEN 1
                WHEN subscription_tier = 'pro' THEN 5
                WHEN subscription_tier = 'agency' THEN 999
                ELSE 1
            END,
            keyword_limit = CASE
                WHEN subscription_tier = 'starter' THEN 20
                WHEN subscription_tier = 'pro' THEN 50
                WHEN subscription_tier = 'agency' THEN 999
                ELSE 5
            END
        """
    )
    op.alter_column("organizations", "plan", server_default=None)
    op.alter_column("organizations", "location_limit", server_default=None)
    op.alter_column("organizations", "keyword_limit", server_default=None)


def downgrade() -> None:
    op.drop_column("organizations", "keyword_limit")
    op.drop_column("organizations", "location_limit")
    op.drop_column("organizations", "plan")
