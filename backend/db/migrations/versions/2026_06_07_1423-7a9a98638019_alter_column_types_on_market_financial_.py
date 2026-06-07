"""Alter column types on market_financial_reports

Revision ID: 7a9a98638019
Revises: ed9b1cff5d86
Create Date: 2026-06-07 14:23:03.211130

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7a9a98638019"
down_revision: Union[str, Sequence[str], None] = "ed9b1cff5d86"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.alter_column(
        "market_financial_reports",
        "adr_usd",
        existing_type=sa.REAL(),
        type_=sa.NUMERIC(),
        existing_nullable=True,
    )
    op.alter_column(
        "market_financial_reports",
        "annual_revenue_usd",
        existing_type=sa.REAL(),
        type_=sa.NUMERIC(),
        existing_nullable=True,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.alter_column(
        "market_financial_reports",
        "annual_revenue_usd",
        existing_type=sa.NUMERIC(),
        type_=sa.REAL(),
        existing_nullable=True,
    )
    op.alter_column(
        "market_financial_reports",
        "adr_usd",
        existing_type=sa.NUMERIC(),
        type_=sa.REAL(),
        existing_nullable=True,
    )
