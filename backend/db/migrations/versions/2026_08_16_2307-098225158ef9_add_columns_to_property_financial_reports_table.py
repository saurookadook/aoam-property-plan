"""Add columns to property_financial_reports table

Revision ID: 098225158ef9
Revises: ac3dd77365d3
Create Date: 2026-08-16 23:07:57.606203

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "098225158ef9"
down_revision: Union[str, Sequence[str], None] = "ac3dd77365d3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        "property_financial_reports",
        sa.Column("airroi_adr_cop", sa.NUMERIC(), nullable=True),
    )
    op.add_column(
        "property_financial_reports",
        sa.Column("airroi_occupancy_rate", sa.REAL(), nullable=True),
    )
    op.add_column(
        "property_financial_reports",
        sa.Column("airroi_revenue_cop", sa.NUMERIC(), nullable=True),
    )
    op.add_column(
        "property_financial_reports",
        sa.Column("airroi_revenue_p25_cop", sa.NUMERIC(), nullable=True),
    )
    op.add_column(
        "property_financial_reports",
        sa.Column("airroi_revenue_p50_cop", sa.NUMERIC(), nullable=True),
    )
    op.add_column(
        "property_financial_reports",
        sa.Column("airroi_revenue_p75_cop", sa.NUMERIC(), nullable=True),
    )
    op.add_column(
        "property_financial_reports",
        sa.Column("airroi_revenue_p90_cop", sa.NUMERIC(), nullable=True),
    )
    op.add_column(
        "property_financial_reports",
        sa.Column("annual_revenue_source", sa.TEXT(), nullable=True),
    )
    op.add_column(
        "property_financial_reports",
        sa.Column("assessed_value_cop", sa.NUMERIC(), nullable=True),
    )
    op.add_column(
        "property_financial_reports",
        sa.Column("closing_costs_percentage", sa.REAL(), nullable=True),
    )
    op.add_column(
        "property_financial_reports",
        sa.Column("comp_count", sa.INTEGER(), nullable=True),
    )
    op.add_column(
        "property_financial_reports",
        sa.Column("comp_derived_revenue_cop", sa.NUMERIC(), nullable=True),
    )
    op.add_column(
        "property_financial_reports",
        sa.Column("hoa_monthly_cop", sa.NUMERIC(), nullable=True),
    )
    op.add_column(
        "property_financial_reports",
        sa.Column("maintenance_reserve_percentage", sa.REAL(), nullable=True),
    )
    op.add_column(
        "property_financial_reports",
        sa.Column("management_fee_percentage", sa.REAL(), nullable=True),
    )
    op.add_column(
        "property_financial_reports",
        sa.Column("monthly_mortgage_cop", sa.NUMERIC(), nullable=True),
    )
    op.add_column(
        "property_financial_reports",
        sa.Column(
            "monthly_revenue_distribution", postgresql.ARRAY(sa.REAL()), nullable=True
        ),
    )
    op.add_column(
        "property_financial_reports",
        sa.Column("peak_months", postgresql.ARRAY(sa.TEXT()), nullable=True),
    )
    op.add_column(
        "property_financial_reports",
        sa.Column("predial_rate_percentage", sa.REAL(), nullable=True),
    )
    op.add_column(
        "property_financial_reports",
        sa.Column("purchase_price_cop", sa.NUMERIC(), nullable=True),
    )
    op.add_column(
        "property_financial_reports",
        sa.Column("renovation_budget_cop", sa.NUMERIC(), nullable=True),
    )
    op.alter_column(
        "property_financial_reports",
        "calculated_at",
        existing_type=postgresql.TIMESTAMP(),
        type_=postgresql.TIMESTAMP(timezone=True),
        existing_nullable=True,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.alter_column(
        "property_financial_reports",
        "calculated_at",
        existing_type=postgresql.TIMESTAMP(timezone=True),
        type_=postgresql.TIMESTAMP(),
        existing_nullable=True,
    )
    op.drop_column("property_financial_reports", "renovation_budget_cop")
    op.drop_column("property_financial_reports", "purchase_price_cop")
    op.drop_column("property_financial_reports", "predial_rate_percentage")
    op.drop_column("property_financial_reports", "peak_months")
    op.drop_column("property_financial_reports", "monthly_revenue_distribution")
    op.drop_column("property_financial_reports", "monthly_mortgage_cop")
    op.drop_column("property_financial_reports", "management_fee_percentage")
    op.drop_column("property_financial_reports", "maintenance_reserve_percentage")
    op.drop_column("property_financial_reports", "hoa_monthly_cop")
    op.drop_column("property_financial_reports", "comp_derived_revenue_cop")
    op.drop_column("property_financial_reports", "comp_count")
    op.drop_column("property_financial_reports", "closing_costs_percentage")
    op.drop_column("property_financial_reports", "assessed_value_cop")
    op.drop_column("property_financial_reports", "annual_revenue_source")
    op.drop_column("property_financial_reports", "airroi_revenue_p90_cop")
    op.drop_column("property_financial_reports", "airroi_revenue_p75_cop")
    op.drop_column("property_financial_reports", "airroi_revenue_p50_cop")
    op.drop_column("property_financial_reports", "airroi_revenue_p25_cop")
    op.drop_column("property_financial_reports", "airroi_revenue_cop")
    op.drop_column("property_financial_reports", "airroi_occupancy_rate")
    op.drop_column("property_financial_reports", "airroi_adr_cop")
