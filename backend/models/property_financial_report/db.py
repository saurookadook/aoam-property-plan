from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column

from db.base_db import BaseDB
from models.mixins import TimestampsDB


class PropertyFinancialReportDB(BaseDB, TimestampsDB):
    property_id: Mapped[UUID] = mapped_column(
        ForeignKey("properties.id"), nullable=True
    )
    annual_net_income_usd: Mapped[float] = mapped_column(postgresql.REAL, nullable=True)
    annual_revenue_usd: Mapped[float] = mapped_column(postgresql.REAL, nullable=True)
    calculated_at: Mapped[datetime] = mapped_column(postgresql.TIMESTAMP, nullable=True)
    cash_invested_usd: Mapped[float] = mapped_column(postgresql.REAL, nullable=True)
    coc_return_percentage: Mapped[float] = mapped_column(postgresql.REAL, nullable=True)
    """
    Cash-on-Cash Return Percentage
    """

    down_payment_percentage: Mapped[float] = mapped_column(
        postgresql.REAL, nullable=True
    )
    exchange_rate: Mapped[float] = mapped_column(postgresql.REAL, nullable=True)
    """
    TODO: should this also have a foreign key reference?
    """

    interest_rate: Mapped[float] = mapped_column(postgresql.REAL, nullable=True)
    loan_term_years: Mapped[float] = mapped_column(postgresql.REAL, nullable=True)
    """
    NOTE: Mapped as a ``float`` to leave room for partial years.
    """

    monthly_expenses_usd: Mapped[float] = mapped_column(postgresql.REAL, nullable=True)
    payback_years: Mapped[float] = mapped_column(postgresql.NUMERIC, nullable=True)
    """
    NOTE: Mapped as a ``float`` to leave room for partial years.
    """
