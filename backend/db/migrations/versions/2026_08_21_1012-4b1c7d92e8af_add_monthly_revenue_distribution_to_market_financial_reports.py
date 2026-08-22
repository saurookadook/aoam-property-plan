"""Add monthly_revenue_distribution to market_financial_reports

Revision ID: 4b1c7d92e8af
Revises: 659ac9cd8aee
Create Date: 2026-08-21 10:12:04.118722

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "4b1c7d92e8af"
down_revision: Union[str, Sequence[str], None] = "659ac9cd8aee"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # Mirrors ``property_financial_reports.monthly_revenue_distribution``, added
    # in ``098225158ef9``. ``handle_markets_peak_months`` already fetches these
    # twelve fractions to derive ``peak_months`` and throws them away; a
    # market-level seasonality view has nowhere to read them from without this.
    op.add_column(
        "market_financial_reports",
        sa.Column(
            "monthly_revenue_distribution", postgresql.ARRAY(sa.REAL()), nullable=True
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_column("market_financial_reports", "monthly_revenue_distribution")
