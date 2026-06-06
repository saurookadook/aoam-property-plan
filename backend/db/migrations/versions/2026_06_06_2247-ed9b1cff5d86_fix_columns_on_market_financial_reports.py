"""Fix columns on market_financial_reports

Revision ID: ed9b1cff5d86
Revises: 38d1d58b35c0
Create Date: 2026-06-06 22:47:47.067585

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "ed9b1cff5d86"
down_revision: Union[str, Sequence[str], None] = "38d1d58b35c0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        "market_financial_reports",
        sa.Column("adr_cop", sa.NUMERIC(), nullable=False),
    )
    op.add_column(
        "market_financial_reports",
        sa.Column("annual_revenue_cop", sa.NUMERIC(), nullable=False),
    )
    op.alter_column(
        "market_financial_reports", "adr_usd", existing_type=sa.REAL(), nullable=True
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.alter_column(
        "market_financial_reports", "adr_usd", existing_type=sa.REAL(), nullable=False
    )
    op.drop_column("market_financial_reports", "annual_revenue_cop")
    op.drop_column("market_financial_reports", "adr_cop")
