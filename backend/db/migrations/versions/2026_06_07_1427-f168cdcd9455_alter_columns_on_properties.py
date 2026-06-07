"""Alter columns on properties

Revision ID: f168cdcd9455
Revises: 7a9a98638019
Create Date: 2026-06-07 14:27:00.284086

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f168cdcd9455"
down_revision: Union[str, Sequence[str], None] = "7a9a98638019"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.alter_column(
        "properties",
        "purchase_price_cop",
        existing_type=sa.BIGINT(),
        type_=sa.NUMERIC(),
        existing_nullable=False,
    )
    op.alter_column(
        "properties", "purchase_price_usd", existing_type=sa.NUMERIC(), nullable=True
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.alter_column(
        "properties", "purchase_price_usd", existing_type=sa.NUMERIC(), nullable=False
    )
    op.alter_column(
        "properties",
        "purchase_price_cop",
        existing_type=sa.NUMERIC(),
        type_=sa.BIGINT(),
        existing_nullable=False,
    )
