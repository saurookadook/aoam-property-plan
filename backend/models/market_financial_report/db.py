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
    adr_cop: Mapped[float] = mapped_column(postgresql.NUMERIC, nullable=False)
    adr_usd: Mapped[float] = mapped_column(postgresql.NUMERIC, nullable=True)
    annual_revenue_cop: Mapped[float] = mapped_column(
        postgresql.NUMERIC, nullable=False
    )
    annual_revenue_usd: Mapped[float] = mapped_column(postgresql.NUMERIC, nullable=True)
    last_updated: Mapped[datetime] = mapped_column(
        postgresql.TIMESTAMP, index=True, nullable=False
    )
    listing_count: Mapped[float] = mapped_column(postgresql.REAL, nullable=False)
    monthly_revenue_distribution: Mapped[list[float]] = mapped_column(
        postgresql.ARRAY(postgresql.REAL), nullable=True
    )
    """
    Twelve fractions summing to 1.0, mirroring the column of the same name on
    ``property_financial_reports``.

    Written by ``handle_markets_peak_months`` from the centroid estimate it
    already makes: ``peak_months`` is the top three names out of these twelve
    numbers, so storing only the names threw away every other month.
    """

    occupancy_rate: Mapped[float] = mapped_column(postgresql.REAL, nullable=False)
    peak_months: Mapped[list[str]] = mapped_column(
        postgresql.ARRAY(postgresql.TEXT), nullable=True
    )
