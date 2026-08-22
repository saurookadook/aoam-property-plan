"""Add market_id to properties table

Revision ID: 7d3ea6c4b915
Revises: 4b1c7d92e8af
Create Date: 2026-08-21 10:18:47.905513

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7d3ea6c4b915"
down_revision: Union[str, Sequence[str], None] = "4b1c7d92e8af"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # Nullable on purpose. ``markets`` carries AirROI's locality while
    # ``properties`` carries whatever Finca Raiz printed on the page, so the two
    # cannot be joined on text - a Pance cabin says ``city: 'Cali'``. This column
    # is the join key, resolved from coordinates at create time, and a property
    # outside every market's listing footprint legitimately has none.
    op.add_column("properties", sa.Column("market_id", sa.UUID(), nullable=True))
    op.create_foreign_key(
        op.f("properties_market_id_fkey"),
        "properties",
        "markets",
        ["market_id"],
        ["id"],
    )
    op.create_index(
        op.f("ix_properties_market_id"), "properties", ["market_id"], unique=False
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(op.f("ix_properties_market_id"), table_name="properties")
    op.drop_constraint(
        op.f("properties_market_id_fkey"), "properties", type_="foreignkey"
    )
    op.drop_column("properties", "market_id")
