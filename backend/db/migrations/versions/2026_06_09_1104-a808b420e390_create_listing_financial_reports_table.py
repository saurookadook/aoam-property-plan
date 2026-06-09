"""Create listing_financial_reports table

Revision ID: a808b420e390
Revises: 2ed52adf264b
Create Date: 2026-06-09 11:04:27.533495

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "a808b420e390"
down_revision: Union[str, Sequence[str], None] = "2ed52adf264b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        "listing_financial_reports",
        sa.Column("listing_id", sa.UUID(), nullable=False),
        sa.Column("adr_cop", sa.NUMERIC(), nullable=False),
        sa.Column("adr_usd", sa.NUMERIC(), nullable=True),
        sa.Column("annual_revenue_cop", sa.NUMERIC(), nullable=False),
        sa.Column("annual_revenue_usd", sa.NUMERIC(), nullable=True),
        sa.Column("occupancy_rate", sa.REAL(), nullable=False),
        sa.Column("number_of_reviews", sa.INTEGER(), nullable=True),
        sa.Column("rating_overall", sa.REAL(), nullable=True),
        sa.Column("rating_accuracy", sa.REAL(), nullable=True),
        sa.Column("rating_checkin", sa.REAL(), nullable=True),
        sa.Column("rating_cleanliness", sa.REAL(), nullable=True),
        sa.Column("rating_communication", sa.REAL(), nullable=True),
        sa.Column("rating_location", sa.REAL(), nullable=True),
        sa.Column("rating_value", sa.REAL(), nullable=True),
        sa.Column("ttm_revenue", sa.NUMERIC(), nullable=True),
        sa.Column("ttm_avg_rate", sa.NUMERIC(), nullable=True),
        sa.Column("ttm_occupancy_rate", sa.REAL(), nullable=True),
        sa.Column("ttm_adjusted_occupancy_rate", sa.REAL(), nullable=True),
        sa.Column("ttm_revpar", sa.NUMERIC(), nullable=True),
        sa.Column("ttm_adjusted_revpar", sa.NUMERIC(), nullable=True),
        sa.Column("ttm_total_days", sa.REAL(), nullable=True),
        sa.Column("ttm_available_days", sa.REAL(), nullable=True),
        sa.Column("ttm_blocked_days", sa.REAL(), nullable=True),
        sa.Column("ttm_days_reserved", sa.REAL(), nullable=True),
        sa.Column("ttm_avg_min_nights", sa.REAL(), nullable=True),
        sa.Column("ttm_avg_length_of_stay", sa.REAL(), nullable=True),
        sa.Column("l90d_revenue", sa.NUMERIC(), nullable=True),
        sa.Column("l90d_avg_rate", sa.NUMERIC(), nullable=True),
        sa.Column("l90d_occupancy_rate", sa.REAL(), nullable=True),
        sa.Column("l90d_adjusted_occupancy_rate", sa.REAL(), nullable=True),
        sa.Column("l90d_revpar", sa.NUMERIC(), nullable=True),
        sa.Column("l90d_adjusted_revpar", sa.NUMERIC(), nullable=True),
        sa.Column("l90d_total_days", sa.REAL(), nullable=True),
        sa.Column("l90d_available_days", sa.REAL(), nullable=True),
        sa.Column("l90d_blocked_days", sa.REAL(), nullable=True),
        sa.Column("l90d_days_reserved", sa.REAL(), nullable=True),
        sa.Column("l90d_avg_min_nights", sa.REAL(), nullable=True),
        sa.Column("l90d_avg_length_of_stay", sa.REAL(), nullable=True),
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
            ["listing_id"],
            ["listings.id"],
            name=op.f("listing_financial_reports_listing_id_fkey"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("listing_financial_reports_pkey")),
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_table("listing_financial_reports")
