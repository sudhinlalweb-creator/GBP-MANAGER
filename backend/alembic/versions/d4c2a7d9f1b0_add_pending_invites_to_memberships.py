"""add pending invite support to organization memberships

Revision ID: d4c2a7d9f1b0
Revises: 8b8a3d1ab7aa
Create Date: 2026-06-22 00:00:01.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "d4c2a7d9f1b0"
down_revision = "8b8a3d1ab7aa"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("organization_memberships", "user_id", nullable=True)
    op.add_column(
        "organization_memberships",
        sa.Column(
            "is_pending",
            sa.Boolean(),
            server_default=sa.false(),
            nullable=False,
        ),
    )
    op.add_column(
        "organization_memberships",
        sa.Column("invited_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.alter_column("organization_memberships", "is_pending", server_default=None)


def downgrade() -> None:
    op.drop_column("organization_memberships", "invited_at")
    op.drop_column("organization_memberships", "is_pending")
    op.alter_column("organization_memberships", "user_id", nullable=False)
