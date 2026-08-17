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
    airroi_adr_cop: Mapped[float] = mapped_column(postgresql.NUMERIC, nullable=True)
    airroi_occupancy_rate: Mapped[float] = mapped_column(postgresql.REAL, nullable=True)
    airroi_revenue_cop: Mapped[float] = mapped_column(postgresql.NUMERIC, nullable=True)
    """
    AirROI's own annual estimate - ``percentiles.revenue.avg``, and therefore a
    mean over a right-skewed distribution rather than a typical outcome.
    """

    airroi_revenue_p25_cop: Mapped[float] = mapped_column(
        postgresql.NUMERIC, nullable=True
    )
    airroi_revenue_p50_cop: Mapped[float] = mapped_column(
        postgresql.NUMERIC, nullable=True
    )
    airroi_revenue_p75_cop: Mapped[float] = mapped_column(
        postgresql.NUMERIC, nullable=True
    )
    airroi_revenue_p90_cop: Mapped[float] = mapped_column(
        postgresql.NUMERIC, nullable=True
    )
    annual_net_income_cop: Mapped[float] = mapped_column(
        postgresql.NUMERIC, nullable=True
    )
    annual_net_income_usd: Mapped[float] = mapped_column(
        postgresql.NUMERIC, nullable=True
    )
    annual_revenue_cop: Mapped[float] = mapped_column(postgresql.NUMERIC, nullable=True)
    annual_revenue_source: Mapped[str] = mapped_column(postgresql.TEXT, nullable=True)
    """
    Which estimate ``annual_revenue_cop`` was taken from, and why. Recorded
    because the comp-derived figure and AirROI's own diverge by market - comps
    run 2x the direct estimate in Bogota and 0.77x in Salento - so a stored
    revenue is uninterpretable without knowing which one produced it.
    """

    annual_revenue_usd: Mapped[float] = mapped_column(postgresql.NUMERIC, nullable=True)
    assessed_value_cop: Mapped[float] = mapped_column(postgresql.NUMERIC, nullable=True)
    """
    Cadastral (avaluo catastral) value predial is levied on, which routinely sits
    below the purchase price.
    """

    calculated_at: Mapped[datetime] = mapped_column(
        postgresql.TIMESTAMP(timezone=True), nullable=True
    )
    cash_invested_cop: Mapped[float] = mapped_column(postgresql.NUMERIC, nullable=True)
    cash_invested_usd: Mapped[float] = mapped_column(postgresql.NUMERIC, nullable=True)
    closing_costs_percentage: Mapped[float] = mapped_column(
        postgresql.REAL, nullable=True
    )
    coc_return_percentage: Mapped[float] = mapped_column(postgresql.REAL, nullable=True)
    """
    Cash-on-Cash Return Percentage
    """

    comp_count: Mapped[int] = mapped_column(postgresql.INTEGER, nullable=True)
    comp_derived_revenue_cop: Mapped[float] = mapped_column(
        postgresql.NUMERIC, nullable=True
    )
    """
    Median of ``adr x occupancy x 365`` over the surviving comps, or ``NULL``
    when too few survived to call it an estimate.
    """

    down_payment_percentage: Mapped[float] = mapped_column(
        postgresql.REAL, nullable=True
    )
    exchange_rate: Mapped[float] = mapped_column(postgresql.REAL, nullable=True)
    """
    TODO: should this also have a foreign key reference?
    """

    hoa_monthly_cop: Mapped[float] = mapped_column(postgresql.NUMERIC, nullable=True)
    interest_rate: Mapped[float] = mapped_column(postgresql.REAL, nullable=True)
    loan_term_years: Mapped[float] = mapped_column(postgresql.REAL, nullable=True)
    """
    NOTE: Mapped as a ``float`` to leave room for partial years.
    """

    maintenance_reserve_percentage: Mapped[float] = mapped_column(
        postgresql.REAL, nullable=True
    )
    management_fee_percentage: Mapped[float] = mapped_column(
        postgresql.REAL, nullable=True
    )
    monthly_expenses_cop: Mapped[float] = mapped_column(
        postgresql.NUMERIC, nullable=True
    )
    monthly_expenses_usd: Mapped[float] = mapped_column(
        postgresql.NUMERIC, nullable=True
    )
    monthly_mortgage_cop: Mapped[float] = mapped_column(
        postgresql.NUMERIC, nullable=True
    )
    monthly_revenue_distribution: Mapped[list[float]] = mapped_column(
        postgresql.ARRAY(postgresql.REAL), nullable=True
    )
    """
    Twelve fractions summing to 1.0, from ``monthly_revenue_distributions`` on
    ``/calculator/estimate``. AirROI publishes no ``/markets/seasonality``
    endpoint; this is the only seasonality it exposes.
    """

    payback_years: Mapped[float] = mapped_column(postgresql.NUMERIC, nullable=True)
    """
    NOTE: Mapped as a ``float`` to leave room for partial years.
    """

    peak_months: Mapped[list[str]] = mapped_column(
        postgresql.ARRAY(postgresql.TEXT), nullable=True
    )
    """
    Full English month names, mirroring ``market_financial_reports.peak_months``.
    """

    predial_rate_percentage: Mapped[float] = mapped_column(
        postgresql.REAL, nullable=True
    )
    purchase_price_cop: Mapped[float] = mapped_column(postgresql.NUMERIC, nullable=True)
    """
    The price the report was run against, kept alongside the result so an
    overridden or later-changed ``properties.purchase_price_cop`` cannot
    retroactively invalidate the arithmetic.
    """

    renovation_budget_cop: Mapped[float] = mapped_column(
        postgresql.NUMERIC, nullable=True
    )
