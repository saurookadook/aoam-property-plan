"""Create property_financial_reports table

Revision ID: 480adc8cacb3
Revises: 9c4b503fe3cf
Create Date: 2026-05-24 18:24:59.908424

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "480adc8cacb3"
down_revision: Union[str, Sequence[str], None] = "9c4b503fe3cf"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        "property_financial_reports",
        sa.Column("property_id", sa.UUID(), nullable=True),
        sa.Column("annual_net_income_usd", sa.REAL(), nullable=True),
        sa.Column("annual_revenue_usd", sa.REAL(), nullable=True),
        sa.Column("calculated_at", postgresql.TIMESTAMP(), nullable=True),
        sa.Column("cash_invested_usd", sa.REAL(), nullable=True),
        sa.Column("coc_return_percentage", sa.REAL(), nullable=True),
        sa.Column("down_payment_pct", sa.REAL(), nullable=True),
        sa.Column("exchange_rate", sa.REAL(), nullable=True),
        sa.Column("interest_rate", sa.REAL(), nullable=True),
        sa.Column("loan_term_years", sa.REAL(), nullable=True),
        sa.Column("monthly_expenses_usd", sa.REAL(), nullable=True),
        sa.Column("payback_years", sa.NUMERIC(), nullable=True),
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
            ["property_id"],
            ["properties.id"],
            name=op.f("property_financial_reports_property_id_fkey"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("property_financial_reports_pkey")),
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_table("property_financial_reports")
