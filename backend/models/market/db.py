from __future__ import annotations

from datetime import datetime

from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column

from db.base_db import BaseDB
from models.mixins import TimestampsDB


class MarketDB(BaseDB, TimestampsDB):
    adr_usd: Mapped[float] = mapped_column(postgresql.REAL, nullable=False)
    annual_revenue_usd: Mapped[float] = mapped_column(postgresql.REAL, nullable=False)
    city: Mapped[str] = mapped_column(postgresql.TEXT, nullable=False)
    country: Mapped[str] = mapped_column(postgresql.TEXT, nullable=False)
    listing_count: Mapped[float] = mapped_column(postgresql.REAL, nullable=False)
    last_updated: Mapped[datetime] = mapped_column(postgresql.TIMESTAMP, nullable=False)
    neighborhood: Mapped[str] = mapped_column(postgresql.TEXT, nullable=True)
    occupancy_rate: Mapped[float] = mapped_column(postgresql.REAL, nullable=False)
    peak_months: Mapped[list[str]] = mapped_column(
        postgresql.ARRAY(postgresql.TEXT), nullable=True
    )
    region: Mapped[str] = mapped_column(postgresql.TEXT, nullable=False)
