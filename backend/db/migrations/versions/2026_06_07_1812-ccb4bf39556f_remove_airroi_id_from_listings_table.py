"""Remove airroi_id from listings table

Revision ID: ccb4bf39556f
Revises: c2a99ea3b9ce
Create Date: 2026-06-07 18:12:21.561142

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "ccb4bf39556f"
down_revision: Union[str, Sequence[str], None] = "c2a99ea3b9ce"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.drop_column("listings", "airroi_id")
    op.create_primary_key(op.f("listings_pkey"), "listings", ["id"])


def downgrade() -> None:
    """Downgrade schema."""

    op.add_column(
        "listings",
        sa.Column("airroi_id", sa.UUID(), autoincrement=False, nullable=False),
    )
    op.drop_constraint(op.f("listings_pkey"), "listings", type_="unique")
    op.create_primary_key(op.f("listings_pkey"), "listings", ["airroi_id", "id"])
