"""Create property_comps table

Revision ID: 659ac9cd8aee
Revises: ec9f47d307c0
Create Date: 2026-08-16 23:24:43.532869

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "659ac9cd8aee"
down_revision: Union[str, Sequence[str], None] = "ec9f47d307c0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "property_comps",
        sa.Column("adr_cop", sa.NUMERIC(), nullable=True),
        sa.Column("captured_at", postgresql.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("distance_km", sa.REAL(), nullable=True),
        sa.Column("listing_id", sa.UUID(), nullable=False),
        sa.Column("occupancy_rate", sa.REAL(), nullable=True),
        sa.Column("property_id", sa.UUID(), nullable=False),
        sa.Column("ttm_revenue_cop", sa.NUMERIC(), nullable=True),
        sa.Column("ttm_total_days", sa.REAL(), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["listing_id"], ["listings.id"], name=op.f("property_comps_listing_id_fkey")
        ),
        sa.ForeignKeyConstraint(
            ["property_id"],
            ["properties.id"],
            name=op.f("property_comps_property_id_fkey"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("property_comps_pkey")),
        sa.UniqueConstraint(
            "property_id",
            "listing_id",
            name=op.f("property_comps_property_id_listing_id_key"),
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("property_comps")
