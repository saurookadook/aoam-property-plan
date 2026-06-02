"""Create market_financial_reports table

Revision ID: cf17c05b00e6
Revises: 6642676892db
Create Date: 2026-05-31 23:17:16.596793

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "cf17c05b00e6"
down_revision: Union[str, Sequence[str], None] = "6642676892db"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        "market_financial_reports",
        sa.Column("market_id", sa.UUID(), nullable=False),
        sa.Column("adr_usd", sa.REAL(), nullable=False),
        sa.Column("annual_revenue_usd", sa.REAL(), nullable=True),
        sa.Column("last_updated", postgresql.TIMESTAMP(), nullable=False),
        sa.Column("listing_count", sa.REAL(), nullable=False),
        sa.Column("occupancy_rate", sa.REAL(), nullable=False),
        sa.Column("peak_months", postgresql.ARRAY(sa.TEXT()), nullable=True),
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
            ["market_id"],
            ["markets.id"],
            name=op.f("market_financial_reports_market_id_fkey"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("market_financial_reports_pkey")),
    )
    op.create_index(
        op.f("ix_market_financial_reports_last_updated"),
        "market_financial_reports",
        ["last_updated"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(
        op.f("ix_market_financial_reports_last_updated"),
        table_name="market_financial_reports",
    )
    op.drop_table("market_financial_reports")
