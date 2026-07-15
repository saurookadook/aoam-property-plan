"""Add fields to listings

Revision ID: 7abfe7783ffd
Revises: fd50b58f027e
Create Date: 2026-07-15 00:20:33.030975

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "7abfe7783ffd"
down_revision: Union[str, Sequence[str], None] = "fd50b58f027e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        "listings",
        sa.Column(
            "amenities",
            postgresql.ARRAY(sa.TEXT()),
            server_default="{}",
            nullable=False,
        ),
    )
    op.add_column("listings", sa.Column("baths", sa.REAL(), nullable=True))
    op.add_column("listings", sa.Column("beds", sa.INTEGER(), nullable=True))
    op.add_column("listings", sa.Column("description", sa.TEXT(), nullable=True))
    op.add_column("listings", sa.Column("name", sa.TEXT(), nullable=True))
    op.add_column(
        "listings",
        sa.Column(
            "photo_urls",
            postgresql.ARRAY(sa.TEXT()),
            server_default="{}",
            nullable=False,
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_column("listings", "photo_urls")
    op.drop_column("listings", "name")
    op.drop_column("listings", "description")
    op.drop_column("listings", "beds")
    op.drop_column("listings", "baths")
    op.drop_column("listings", "amenities")
