"""add processed_webhook_events table for Stripe idempotency

Revision ID: e1f2a3b4c5d6
Revises: f0e1d2c3b4a5
Create Date: 2026-06-22
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "e1f2a3b4c5d6"
# Merges the two pre-existing branch heads into a single linear chain
down_revision = ("f0e1d2c3b4a5", "d5e6f7a8b9c0")
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "processed_webhook_events",
        sa.Column("event_id", sa.String(255), primary_key=True),
        sa.Column("event_type", sa.String(128), nullable=False),
        sa.Column(
            "processed_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_table("processed_webhook_events")
