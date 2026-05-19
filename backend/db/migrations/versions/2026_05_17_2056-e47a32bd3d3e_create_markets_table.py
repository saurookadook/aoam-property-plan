"""Create markets table

Revision ID: e47a32bd3d3e
Revises:
Create Date: 2026-05-17 20:56:56.104876

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "e47a32bd3d3e"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "markets",
        sa.Column("city", sa.TEXT(), nullable=False),
        sa.Column("neighborhood", sa.TEXT(), nullable=False),
        sa.Column("country", sa.TEXT(), nullable=False),
        sa.Column("adr_usd", sa.REAL(), nullable=False),
        sa.Column("occupancy_rate", sa.REAL(), nullable=False),
        sa.Column("annual_revenue_usd", sa.REAL(), nullable=False),
        sa.Column("peak_months", postgresql.ARRAY(sa.TEXT()), nullable=False),
        sa.Column("listing_count", sa.INTEGER(), nullable=False),
        sa.Column("last_updated", postgresql.TIMESTAMP(), nullable=False),
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
        sa.PrimaryKeyConstraint("id", name=op.f("market_pkey")),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("markets")
