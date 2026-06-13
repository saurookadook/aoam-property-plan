"""Remove columns from listing_financial_reports

Revision ID: d33d6d5dedaa
Revises: a808b420e390
Create Date: 2026-06-12 00:34:16.536706

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d33d6d5dedaa"
down_revision: Union[str, Sequence[str], None] = "a808b420e390"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.drop_column("listing_financial_reports", "adr_usd")
    op.drop_column("listing_financial_reports", "occupancy_rate")
    op.drop_column("listing_financial_reports", "annual_revenue_cop")
    op.drop_column("listing_financial_reports", "adr_cop")
    op.drop_column("listing_financial_reports", "annual_revenue_usd")


def downgrade() -> None:
    """Downgrade schema."""

    op.add_column(
        "listing_financial_reports",
        sa.Column(
            "annual_revenue_usd", sa.NUMERIC(), autoincrement=False, nullable=True
        ),
    )
    op.add_column(
        "listing_financial_reports",
        sa.Column("adr_cop", sa.NUMERIC(), autoincrement=False, nullable=False),
    )
    op.add_column(
        "listing_financial_reports",
        sa.Column(
            "annual_revenue_cop", sa.NUMERIC(), autoincrement=False, nullable=False
        ),
    )
    op.add_column(
        "listing_financial_reports",
        sa.Column("occupancy_rate", sa.REAL(), autoincrement=False, nullable=False),
    )
    op.add_column(
        "listing_financial_reports",
        sa.Column("adr_usd", sa.NUMERIC(), autoincrement=False, nullable=True),
    )
