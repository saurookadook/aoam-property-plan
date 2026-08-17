from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import Field

from models.base.entity import BaseEntityModel
from models.mixins import TimestampsEntityMixin


class PropertyFinancialReportEntity(BaseEntityModel, TimestampsEntityMixin):
    property_id: UUID
    airroi_adr_cop: Optional[float]
    airroi_occupancy_rate: Optional[float]
    airroi_revenue_cop: Optional[float] = Field(
        ...,
        description=(
            "AirROI's own annual estimate - ``percentiles.revenue.avg``, and "
            "therefore a mean over a right-skewed distribution rather than a "
            "typical outcome."
        ),
    )
    """
    AirROI's own annual estimate - ``percentiles.revenue.avg``, and therefore a
    mean over a right-skewed distribution rather than a typical outcome.
    """

    airroi_revenue_p25_cop: Optional[float]
    airroi_revenue_p50_cop: Optional[float]
    airroi_revenue_p75_cop: Optional[float]
    airroi_revenue_p90_cop: Optional[float]
    annual_net_income_cop: Optional[float]
    annual_net_income_usd: Optional[float]
    annual_revenue_cop: Optional[float]
    annual_revenue_source: Optional[str] = Field(
        ...,
        description=("Which estimate ``annual_revenue_cop`` was taken from, and why."),
    )
    """
    Which estimate ``annual_revenue_cop`` was taken from, and why. Recorded
    because the comp-derived figure and AirROI's own diverge by market, so a
    stored revenue is uninterpretable without knowing which one produced it.
    """

    annual_revenue_usd: Optional[float]
    assessed_value_cop: Optional[float] = Field(
        ...,
        description=(
            "Cadastral (avaluo catastral) value predial is levied on, which "
            "routinely sits below the purchase price."
        ),
    )
    """
    Cadastral (avaluo catastral) value predial is levied on, which routinely sits
    below the purchase price.
    """

    calculated_at: datetime
    cash_invested_cop: Optional[float]
    cash_invested_usd: Optional[float]
    closing_costs_percentage: Optional[float]
    coc_return_percentage: Optional[float] = Field(
        ..., description="Cash-on-Cash Return Percentage"
    )
    """
    Cash-on-Cash Return Percentage
    """

    comp_count: Optional[int]
    comp_derived_revenue_cop: Optional[float] = Field(
        ...,
        description=(
            "Median of ``adr x occupancy x 365`` over the surviving comps, or "
            "``None`` when too few survived to call it an estimate."
        ),
    )
    """
    Median of ``adr x occupancy x 365`` over the surviving comps, or ``None``
    when too few survived to call it an estimate.
    """

    down_payment_percentage: Optional[float]
    # TODO: should this also have a foreign key reference?
    exchange_rate: Optional[float]
    hoa_monthly_cop: Optional[float]
    interest_rate: Optional[float]
    loan_term_years: Optional[float] = Field(
        ..., description="NOTE: Mapped as a ``float`` to leave room for partial years."
    )
    """
    NOTE: Mapped as a ``float`` to leave room for partial years.
    """

    maintenance_reserve_percentage: Optional[float]
    management_fee_percentage: Optional[float]
    monthly_expenses_cop: Optional[float]
    monthly_expenses_usd: Optional[float]
    monthly_mortgage_cop: Optional[float]
    monthly_revenue_distribution: Optional[list[float]] = Field(
        ...,
        description=(
            "Twelve fractions summing to 1.0 - the only seasonality AirROI " "exposes."
        ),
    )
    """
    Twelve fractions summing to 1.0, from ``monthly_revenue_distributions`` on
    ``/calculator/estimate``. AirROI publishes no ``/markets/seasonality``
    endpoint; this is the only seasonality it exposes.
    """

    payback_years: Optional[float] = Field(
        ..., description="NOTE: Mapped as a ``float`` to leave room for partial years."
    )
    """
    NOTE: Mapped as a ``float`` to leave room for partial years.
    """

    peak_months: Optional[list[str]] = Field(
        ..., description="Full English month names."
    )
    """
    Full English month names, mirroring ``market_financial_reports.peak_months``.
    """

    predial_rate_percentage: Optional[float]
    purchase_price_cop: Optional[float] = Field(
        ...,
        description=(
            "The price the report was run against, kept alongside the result so "
            "a later change to the property cannot invalidate the arithmetic."
        ),
    )
    """
    The price the report was run against, kept alongside the result so an
    overridden or later-changed ``properties.purchase_price_cop`` cannot
    retroactively invalidate the arithmetic.
    """

    renovation_budget_cop: Optional[float]
