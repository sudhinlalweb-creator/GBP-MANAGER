"""add organization billing fields

Revision ID: 8b8a3d1ab7aa
Revises: c5d0fcafa90a
Create Date: 2026-06-22 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "8b8a3d1ab7aa"
down_revision = "c5d0fcafa90a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("organizations", sa.Column("billing_email", sa.String(length=320), nullable=True))
    op.add_column("organizations", sa.Column("stripe_customer_id", sa.String(length=255), nullable=True))
    op.add_column(
        "organizations",
        sa.Column("stripe_subscription_id", sa.String(length=255), nullable=True),
    )
    op.add_column("organizations", sa.Column("stripe_price_id", sa.String(length=255), nullable=True))
    op.add_column(
        "organizations",
        sa.Column(
            "subscription_status",
            sa.String(length=50),
            server_default="trialing",
            nullable=False,
        ),
    )
    op.add_column(
        "organizations",
        sa.Column("trial_ends_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "organizations",
        sa.Column(
            "subscription_current_period_end",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )
    op.add_column(
        "organizations",
        sa.Column(
            "cancel_at_period_end",
            sa.Boolean(),
            server_default=sa.false(),
            nullable=False,
        ),
    )
    op.create_index(
        op.f("ix_organizations_stripe_customer_id"),
        "organizations",
        ["stripe_customer_id"],
        unique=True,
    )
    op.create_index(
        op.f("ix_organizations_stripe_subscription_id"),
        "organizations",
        ["stripe_subscription_id"],
        unique=True,
    )
    op.alter_column("organizations", "subscription_status", server_default=None)
    op.alter_column("organizations", "cancel_at_period_end", server_default=None)


def downgrade() -> None:
    op.drop_index(op.f("ix_organizations_stripe_subscription_id"), table_name="organizations")
    op.drop_index(op.f("ix_organizations_stripe_customer_id"), table_name="organizations")
    op.drop_column("organizations", "cancel_at_period_end")
    op.drop_column("organizations", "subscription_current_period_end")
    op.drop_column("organizations", "trial_ends_at")
    op.drop_column("organizations", "subscription_status")
    op.drop_column("organizations", "stripe_price_id")
    op.drop_column("organizations", "stripe_subscription_id")
    op.drop_column("organizations", "stripe_customer_id")
    op.drop_column("organizations", "billing_email")
