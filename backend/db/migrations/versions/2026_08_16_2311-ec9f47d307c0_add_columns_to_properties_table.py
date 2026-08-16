"""Add columns to properties table

Revision ID: ec9f47d307c0
Revises: 098225158ef9
Create Date: 2026-08-16 23:11:19.290360

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "ec9f47d307c0"
down_revision: Union[str, Sequence[str], None] = "098225158ef9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column("properties", sa.Column("baths", sa.REAL(), nullable=True))
    op.add_column("properties", sa.Column("guests", sa.INTEGER(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_column("properties", "guests")
    op.drop_column("properties", "baths")
