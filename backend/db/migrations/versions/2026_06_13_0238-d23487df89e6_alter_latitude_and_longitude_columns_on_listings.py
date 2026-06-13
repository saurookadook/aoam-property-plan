"""Alter latitude and longitude columns on listings

Revision ID: d23487df89e6
Revises: 660944b07c89
Create Date: 2026-06-13 02:38:29.403641

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d23487df89e6"
down_revision: Union[str, Sequence[str], None] = "660944b07c89"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.alter_column(
        "listings",
        "latitude",
        existing_type=sa.REAL(),
        type_=sa.DOUBLE_PRECISION(),
        existing_nullable=False,
    )
    op.alter_column(
        "listings",
        "longitude",
        existing_type=sa.REAL(),
        type_=sa.DOUBLE_PRECISION(),
        existing_nullable=False,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.alter_column(
        "listings",
        "longitude",
        existing_type=sa.DOUBLE_PRECISION(),
        type_=sa.REAL(),
        existing_nullable=False,
    )
    op.alter_column(
        "listings",
        "latitude",
        existing_type=sa.DOUBLE_PRECISION(),
        type_=sa.REAL(),
        existing_nullable=False,
    )
