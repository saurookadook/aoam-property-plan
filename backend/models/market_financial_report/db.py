from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column


from db.base_db import BaseDB
from models.mixins import TimestampsDB


class MarketFinancialReportDB(BaseDB, TimestampsDB):
    market_id: Mapped[UUID] = mapped_column(ForeignKey("markets.id"), nullable=False)
    adr_usd: Mapped[float] = mapped_column(postgresql.REAL, nullable=False)
    annual_revenue_usd: Mapped[float] = mapped_column(postgresql.REAL, nullable=True)
    last_updated: Mapped[datetime] = mapped_column(
        postgresql.TIMESTAMP, index=True, nullable=False
    )
    listing_count: Mapped[float] = mapped_column(postgresql.REAL, nullable=False)
    occupancy_rate: Mapped[float] = mapped_column(postgresql.REAL, nullable=False)
    peak_months: Mapped[list[str]] = mapped_column(
        postgresql.ARRAY(postgresql.TEXT), nullable=True
    )
