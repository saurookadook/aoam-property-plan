"""Add index on listings.location column

Revision ID: 9f51ee852a2f
Revises: 9522f52225a6
Create Date: 2026-05-24 20:50:55.889291

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "9f51ee852a2f"
down_revision: Union[str, Sequence[str], None] = "9522f52225a6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_index(
        "ix_listings_location",
        "listings",
        ["location"],
        postgresql_using="gist",
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(
        "ix_listings_location",
        column_name="location",
        postgresql_using="gist",
        table_name="listings",
    )
