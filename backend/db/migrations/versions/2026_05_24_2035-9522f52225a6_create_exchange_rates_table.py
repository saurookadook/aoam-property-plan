"""Create exchange_rates table

Revision ID: 9522f52225a6
Revises: 480adc8cacb3
Create Date: 2026-05-24 20:35:20.869415

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "9522f52225a6"
down_revision: Union[str, Sequence[str], None] = "480adc8cacb3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        "exchange_rates",
        sa.Column("record_date", sa.DATE(), nullable=False),
        sa.Column("cop_per_usd", sa.REAL(), nullable=False),
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
        sa.PrimaryKeyConstraint("record_date", "id", name=op.f("exchange_rates_pkey")),
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_table("exchange_rates")
