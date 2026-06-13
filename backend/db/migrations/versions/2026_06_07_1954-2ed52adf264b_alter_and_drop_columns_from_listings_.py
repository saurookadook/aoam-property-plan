"""Alter and drop columns from listings table

Revision ID: 2ed52adf264b
Revises: 44f2ae3d9364
Create Date: 2026-06-07 19:54:17.519106

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2ed52adf264b"
down_revision: Union[str, Sequence[str], None] = "44f2ae3d9364"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.alter_column("listings", "source_url", existing_type=sa.TEXT(), nullable=True)
    op.drop_column("listings", "adr_cop")
    op.drop_column("listings", "annual_revenue_usd")
    op.drop_column("listings", "annual_revenue_cop")
    op.drop_column("listings", "adr_usd")
    op.drop_column("listings", "occupancy_rate")


def downgrade() -> None:
    """Downgrade schema."""

    op.add_column(
        "listings",
        sa.Column("occupancy_rate", sa.REAL(), autoincrement=False, nullable=False),
    )
    op.add_column(
        "listings",
        sa.Column("adr_usd", sa.NUMERIC(), autoincrement=False, nullable=True),
    )
    op.add_column(
        "listings",
        sa.Column(
            "annual_revenue_cop", sa.NUMERIC(), autoincrement=False, nullable=False
        ),
    )
    op.add_column(
        "listings",
        sa.Column(
            "annual_revenue_usd", sa.NUMERIC(), autoincrement=False, nullable=True
        ),
    )
    op.add_column(
        "listings",
        sa.Column("adr_cop", sa.NUMERIC(), autoincrement=False, nullable=False),
    )
    op.alter_column("listings", "source_url", existing_type=sa.TEXT(), nullable=False)
