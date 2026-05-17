from __future__ import annotations

from uuid import UUID

from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column

from backend.db.base_db import BaseDB
from backend.models.mixins import TimestampsDB


class MarketDB(BaseDB, TimestampsDB):
    id: Mapped[UUID] = mapped_column(
        postgresql.UUID(as_uuid=True), primary_key=True, nullable=False
    )
    city: Mapped[str] = mapped_column(postgresql.TEXT, nullable=False)
    neighborhood: Mapped[str] = mapped_column(postgresql.TEXT, nullable=False)
    country: Mapped[str] = mapped_column(postgresql.TEXT, nullable=False)
    adr_usd: Mapped[float] = mapped_column(postgresql.REAL, nullable=False)
    occupancy_rate: Mapped[float] = mapped_column(postgresql.REAL, nullable=False)
    annual_revenue_usd: Mapped[float] = mapped_column(postgresql.REAL, nullable=False)
    peak_months: Mapped[list[str]] = mapped_column(
        postgresql.ARRAY(postgresql.TEXT), nullable=False
    )
    listing_count: Mapped[int] = mapped_column(postgresql.INTEGER, nullable=False)
    last_updated: Mapped[str] = mapped_column(postgresql.TIMESTAMP, nullable=False)
