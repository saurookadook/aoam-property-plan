"""Alter markets.listing_count column

Revision ID: 6642676892db
Revises: 7e34442bbd43
Create Date: 2026-05-30 23:32:30.528841

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "6642676892db"
down_revision: Union[str, Sequence[str], None] = "7e34442bbd43"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.alter_column(
        "markets",
        "listing_count",
        existing_type=sa.INTEGER(),
        type_=sa.REAL(),
        existing_nullable=False,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.alter_column(
        "markets",
        "listing_count",
        existing_type=sa.REAL(),
        type_=sa.INTEGER(),
        existing_nullable=False,
    )
