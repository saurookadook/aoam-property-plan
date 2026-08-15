"""Add and alter columns to properties table

Revision ID: ac3dd77365d3
Revises: 7abfe7783ffd
Create Date: 2026-08-15 18:07:31.125708

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "ac3dd77365d3"
down_revision: Union[str, Sequence[str], None] = "7abfe7783ffd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        "properties",
        sa.Column(
            "amenities",
            postgresql.ARRAY(sa.TEXT()),
            server_default=sa.text("'{}'::text[]"),
            nullable=False,
        ),
    )
    op.add_column("properties", sa.Column("description", sa.TEXT(), nullable=True))
    op.add_column("properties", sa.Column("name", sa.TEXT(), nullable=True))
    op.add_column(
        "properties",
        sa.Column(
            "status",
            sa.TEXT(),
            server_default=sa.text("'active'"),
            nullable=False,
        ),
    )
    op.alter_column("properties", "postal_code", existing_type=sa.TEXT(), nullable=True)
    op.alter_column(
        "properties", "purchase_price_cop", existing_type=sa.NUMERIC(), nullable=True
    )
    op.create_unique_constraint(
        op.f("properties_source_url_key"), "properties", ["source_url"]
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_constraint(op.f("properties_source_url_key"), "properties", type_="unique")
    op.alter_column(
        "properties", "purchase_price_cop", existing_type=sa.NUMERIC(), nullable=False
    )
    op.alter_column(
        "properties", "postal_code", existing_type=sa.TEXT(), nullable=False
    )
    op.drop_column("properties", "status")
    op.drop_column("properties", "name")
    op.drop_column("properties", "description")
    op.drop_column("properties", "amenities")
