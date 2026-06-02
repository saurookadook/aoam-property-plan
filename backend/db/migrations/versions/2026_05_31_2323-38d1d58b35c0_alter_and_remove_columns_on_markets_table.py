"""Alter and remove columns on markets table

Revision ID: 38d1d58b35c0
Revises: cf17c05b00e6
Create Date: 2026-05-31 23:23:38.474371

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "38d1d58b35c0"
down_revision: Union[str, Sequence[str], None] = "cf17c05b00e6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.alter_column("markets", "city", new_column_name="locality")
    op.alter_column("markets", "neighborhood", new_column_name="district")
    op.drop_column("markets", "annual_revenue_usd")
    op.drop_column("markets", "occupancy_rate")
    op.drop_column("markets", "adr_usd")
    op.drop_column("markets", "listing_count")
    op.drop_column("markets", "last_updated")
    op.drop_column("markets", "peak_months")


def downgrade() -> None:
    """Downgrade schema."""

    op.add_column(
        "markets",
        sa.Column(
            "peak_months",
            postgresql.ARRAY(sa.TEXT()),
            autoincrement=False,
            nullable=True,
        ),
    )
    op.add_column(
        "markets",
        sa.Column(
            "last_updated",
            postgresql.TIMESTAMP(),
            autoincrement=False,
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.add_column(
        "markets",
        sa.Column("listing_count", sa.REAL(), autoincrement=False, nullable=True),
    )
    op.add_column(
        "markets", sa.Column("adr_usd", sa.REAL(), autoincrement=False, nullable=True)
    )
    op.add_column(
        "markets",
        sa.Column("occupancy_rate", sa.REAL(), autoincrement=False, nullable=True),
    )
    op.add_column(
        "markets",
        sa.Column("annual_revenue_usd", sa.REAL(), autoincrement=False, nullable=True),
    )
    op.alter_column("markets", "locality", new_column_name="city")
    op.alter_column("markets", "district", new_column_name="neighborhood")
