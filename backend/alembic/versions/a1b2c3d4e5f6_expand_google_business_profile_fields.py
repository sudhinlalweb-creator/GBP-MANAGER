"""expand google business profile fields

Revision ID: a1b2c3d4e5f6
Revises: f0e1d2c3b4a5
Create Date: 2026-06-22 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "a1b2c3d4e5f6"
down_revision = "f0e1d2c3b4a5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("google_business_profiles", sa.Column("store_code", sa.String(255), nullable=True))
    op.add_column("google_business_profiles", sa.Column("phone_number", sa.String(50), nullable=True))
    op.add_column("google_business_profiles", sa.Column("address_formatted", sa.Text(), nullable=True))
    op.add_column("google_business_profiles", sa.Column("address_street", sa.String(255), nullable=True))
    op.add_column("google_business_profiles", sa.Column("address_city", sa.String(255), nullable=True))
    op.add_column("google_business_profiles", sa.Column("address_state", sa.String(255), nullable=True))
    op.add_column("google_business_profiles", sa.Column("address_postal_code", sa.String(20), nullable=True))
    op.add_column("google_business_profiles", sa.Column("address_country_code", sa.String(10), nullable=True))
    op.add_column("google_business_profiles", sa.Column("latitude", sa.Float(), nullable=True))
    op.add_column("google_business_profiles", sa.Column("longitude", sa.Float(), nullable=True))
    op.add_column("google_business_profiles", sa.Column("maps_url", sa.String(2048), nullable=True))
    op.add_column("google_business_profiles", sa.Column("is_verified", sa.Boolean(), nullable=False, server_default="false"))
    op.add_column("google_business_profiles", sa.Column("is_suspended", sa.Boolean(), nullable=False, server_default="false"))
    op.add_column("google_business_profiles", sa.Column("is_disconnected", sa.Boolean(), nullable=False, server_default="false"))
    op.add_column("google_business_profiles", sa.Column("review_count", sa.Integer(), nullable=True))
    op.add_column("google_business_profiles", sa.Column("average_rating", sa.Float(), nullable=True))
    op.add_column("google_business_profiles", sa.Column("total_photos", sa.Integer(), nullable=True))
    op.add_column("google_business_profiles", sa.Column("completeness_score", sa.Integer(), nullable=True))
    op.add_column("google_business_profiles", sa.Column(
        "raw_api_data",
        postgresql.JSONB(astext_type=sa.Text()),
        nullable=True,
    ))
    op.add_column("google_business_profiles", sa.Column(
        "last_synced_at",
        sa.DateTime(timezone=True),
        nullable=True,
    ))
    op.add_column("google_business_profiles", sa.Column("sync_error", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("google_business_profiles", "sync_error")
    op.drop_column("google_business_profiles", "last_synced_at")
    op.drop_column("google_business_profiles", "raw_api_data")
    op.drop_column("google_business_profiles", "completeness_score")
    op.drop_column("google_business_profiles", "total_photos")
    op.drop_column("google_business_profiles", "average_rating")
    op.drop_column("google_business_profiles", "review_count")
    op.drop_column("google_business_profiles", "is_disconnected")
    op.drop_column("google_business_profiles", "is_suspended")
    op.drop_column("google_business_profiles", "is_verified")
    op.drop_column("google_business_profiles", "maps_url")
    op.drop_column("google_business_profiles", "longitude")
    op.drop_column("google_business_profiles", "latitude")
    op.drop_column("google_business_profiles", "address_country_code")
    op.drop_column("google_business_profiles", "address_postal_code")
    op.drop_column("google_business_profiles", "address_state")
    op.drop_column("google_business_profiles", "address_city")
    op.drop_column("google_business_profiles", "address_street")
    op.drop_column("google_business_profiles", "address_formatted")
    op.drop_column("google_business_profiles", "phone_number")
    op.drop_column("google_business_profiles", "store_code")
