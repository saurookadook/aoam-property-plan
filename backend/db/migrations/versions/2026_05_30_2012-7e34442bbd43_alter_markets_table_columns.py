"""Alter markets table columns

Revision ID: 7e34442bbd43
Revises: 9f51ee852a2f
Create Date: 2026-05-30 20:12:51.021780

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "7e34442bbd43"
down_revision: Union[str, Sequence[str], None] = "9f51ee852a2f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column("markets", sa.Column("region", sa.TEXT(), nullable=False))
    op.alter_column("markets", "neighborhood", existing_type=sa.TEXT(), nullable=True)
    op.alter_column(
        "markets",
        "peak_months",
        existing_type=postgresql.ARRAY(sa.TEXT()),
        nullable=True,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.alter_column(
        "markets",
        "peak_months",
        existing_type=postgresql.ARRAY(sa.TEXT()),
        nullable=False,
    )
    op.alter_column("markets", "neighborhood", existing_type=sa.TEXT(), nullable=False)
    op.drop_column("markets", "region")
