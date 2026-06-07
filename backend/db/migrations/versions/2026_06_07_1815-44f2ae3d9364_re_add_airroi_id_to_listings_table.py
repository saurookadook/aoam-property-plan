"""Re-add airroi_id to listings table

Revision ID: 44f2ae3d9364
Revises: ccb4bf39556f
Create Date: 2026-06-07 18:15:03.770952

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "44f2ae3d9364"
down_revision: Union[str, Sequence[str], None] = "ccb4bf39556f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column("listings", sa.Column("airroi_id", sa.BIGINT(), nullable=False))
    op.create_unique_constraint(
        op.f("listings_airroi_id_key"), "listings", ["airroi_id"]
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_constraint(op.f("listings_airroi_id_key"), "listings", type_="unique")
    op.drop_column("listings", "airroi_id")
