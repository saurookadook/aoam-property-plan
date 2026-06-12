"""Add cover_photo_url column to listings table

Revision ID: 660944b07c89
Revises: d33d6d5dedaa
Create Date: 2026-06-12 13:27:05.441802

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "660944b07c89"
down_revision: Union[str, Sequence[str], None] = "d33d6d5dedaa"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column("listings", sa.Column("cover_photo_url", sa.TEXT(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_column("listings", "cover_photo_url")
