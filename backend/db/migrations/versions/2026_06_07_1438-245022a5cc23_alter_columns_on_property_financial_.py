"""Alter columns on property_financial_reports

Revision ID: 245022a5cc23
Revises: f168cdcd9455
Create Date: 2026-06-07 14:38:18.686762

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "245022a5cc23"
down_revision: Union[str, Sequence[str], None] = "f168cdcd9455"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        "property_financial_reports",
        sa.Column("annual_net_income_cop", sa.NUMERIC(), nullable=True),
    )
    op.add_column(
        "property_financial_reports",
        sa.Column("annual_revenue_cop", sa.NUMERIC(), nullable=True),
    )
    op.add_column(
        "property_financial_reports",
        sa.Column("cash_invested_cop", sa.NUMERIC(), nullable=True),
    )
    op.add_column(
        "property_financial_reports",
        sa.Column("monthly_expenses_cop", sa.NUMERIC(), nullable=True),
    )
    op.alter_column(
        "property_financial_reports",
        "annual_net_income_usd",
        existing_type=sa.REAL(),
        type_=sa.NUMERIC(),
        existing_nullable=True,
    )
    op.alter_column(
        "property_financial_reports",
        "annual_revenue_usd",
        existing_type=sa.REAL(),
        type_=sa.NUMERIC(),
        existing_nullable=True,
    )
    op.alter_column(
        "property_financial_reports",
        "cash_invested_usd",
        existing_type=sa.REAL(),
        type_=sa.NUMERIC(),
        existing_nullable=True,
    )
    op.alter_column(
        "property_financial_reports",
        "monthly_expenses_usd",
        existing_type=sa.REAL(),
        type_=sa.NUMERIC(),
        existing_nullable=True,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.alter_column(
        "property_financial_reports",
        "monthly_expenses_usd",
        existing_type=sa.NUMERIC(),
        type_=sa.REAL(),
        existing_nullable=True,
    )
    op.alter_column(
        "property_financial_reports",
        "cash_invested_usd",
        existing_type=sa.NUMERIC(),
        type_=sa.REAL(),
        existing_nullable=True,
    )
    op.alter_column(
        "property_financial_reports",
        "annual_revenue_usd",
        existing_type=sa.NUMERIC(),
        type_=sa.REAL(),
        existing_nullable=True,
    )
    op.alter_column(
        "property_financial_reports",
        "annual_net_income_usd",
        existing_type=sa.NUMERIC(),
        type_=sa.REAL(),
        existing_nullable=True,
    )
    op.drop_column("property_financial_reports", "monthly_expenses_cop")
    op.drop_column("property_financial_reports", "cash_invested_cop")
    op.drop_column("property_financial_reports", "annual_revenue_cop")
    op.drop_column("property_financial_reports", "annual_net_income_cop")
