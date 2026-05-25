"""Create add bedrooms columns to properties

Revision ID: 9c4b503fe3cf
Revises: 936a81ab0f9a
Create Date: 2026-05-24 17:36:07.656583

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "9c4b503fe3cf"
down_revision: Union[str, Sequence[str], None] = "936a81ab0f9a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column("properties", sa.Column("bedrooms", sa.INTEGER(), nullable=False))


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_column("properties", "bedrooms")
