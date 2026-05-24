"""Create properties table

Revision ID: 936a81ab0f9a
Revises: 3b0f82fc9010
Create Date: 2026-05-24 16:05:39.166659

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "936a81ab0f9a"
down_revision: Union[str, Sequence[str], None] = "3b0f82fc9010"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        "properties",
        sa.Column("address", sa.TEXT(), nullable=False),
        sa.Column("city", sa.TEXT(), nullable=False),
        sa.Column("country", sa.TEXT(), nullable=False),
        sa.Column("latitude", sa.REAL(), nullable=False),
        sa.Column("longitude", sa.REAL(), nullable=False),
        sa.Column("neighborhood", sa.TEXT(), nullable=False),
        sa.Column("notes", sa.String(), nullable=True),
        sa.Column("postal_code", sa.TEXT(), nullable=False),
        sa.Column("property_type", sa.TEXT(), nullable=False),
        sa.Column("purchase_price_cop", sa.BIGINT(), nullable=False),
        sa.Column("purchase_price_usd", sa.NUMERIC(), nullable=False),
        sa.Column("source_created_at", postgresql.TIMESTAMP(), nullable=False),
        sa.Column("source_url", sa.TEXT(), nullable=False),
        sa.Column("state", sa.TEXT(), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            postgresql.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("properties_pkey")),
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_table("properties")
