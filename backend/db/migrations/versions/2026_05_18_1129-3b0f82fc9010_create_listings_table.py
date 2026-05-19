"""Create listings table

Revision ID: 3b0f82fc9010
Revises: e47a32bd3d3e
Create Date: 2026-05-18 11:29:20.063778

"""

from typing import Sequence, Union

import geoalchemy2
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "3b0f82fc9010"
down_revision: Union[str, Sequence[str], None] = "e47a32bd3d3e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "listings",
        sa.Column("adr_usd", sa.REAL(), nullable=False),
        sa.Column("airroi_id", sa.UUID(), nullable=False),
        sa.Column("annual_revenue_usd", sa.REAL(), nullable=False),
        sa.Column("bedrooms", sa.INTEGER(), nullable=False),
        sa.Column("latitude", sa.REAL(), nullable=False),
        sa.Column(
            "location",
            geoalchemy2.types.Geography(
                geometry_type="POINT",
                srid=4326,
                dimension=2,
                from_text="ST_GeogFromText",
                name="geography",
                nullable=False,
            ),
            nullable=False,
        ),
        sa.Column("longitude", sa.REAL(), nullable=False),
        sa.Column("market_id", sa.UUID(), nullable=True),
        sa.Column("occupancy_rate", sa.REAL(), nullable=False),
        sa.Column("property_type", sa.TEXT(), nullable=False),
        sa.Column("source_url", sa.TEXT(), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            postgresql.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["market_id"], ["markets.id"], name=op.f("listings_market_id_fkey")
        ),
        sa.PrimaryKeyConstraint("airroi_id", "id", name=op.f("listings_pkey")),
    )
    # op.create_index(
    #     "idx_listings_location",
    #     "listings",
    #     ["location"],
    #     unique=False,
    #     postgresql_using="gist",
    # )
    # op.drop_table('spatial_ref_sys')


def downgrade() -> None:
    """Downgrade schema."""
    # op.create_table('spatial_ref_sys',
    # sa.Column('srid', sa.INTEGER(), autoincrement=False, nullable=False),
    # sa.Column('auth_name', sa.VARCHAR(length=256), autoincrement=False, nullable=True),
    # sa.Column('auth_srid', sa.INTEGER(), autoincrement=False, nullable=True),
    # sa.Column('srtext', sa.VARCHAR(length=2048), autoincrement=False, nullable=True),
    # sa.Column('proj4text', sa.VARCHAR(length=2048), autoincrement=False, nullable=True),
    # sa.CheckConstraint('srid > 0 AND srid <= 998999', name=op.f('spatial_ref_sys_srid_check')),
    # sa.PrimaryKeyConstraint('srid', name=op.f('spatial_ref_sys_pkey'))
    # )
    # op.drop_index(
    #     "idx_listings_location", table_name="listings", postgresql_using="gist"
    # )
    op.drop_table("listings")
