from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import Field

from models.base.entity import BaseEntityModel
from models.mixins import TimestampsEntityMixin


class PropertyFinancialReportEntity(BaseEntityModel, TimestampsEntityMixin):
    property_id: UUID
    annual_net_income_cop: Optional[float]
    annual_net_income_usd: Optional[float]
    annual_revenue_cop: Optional[float]
    annual_revenue_usd: Optional[float]
    calculated_at: datetime
    cash_invested_cop: Optional[float]
    cash_invested_usd: Optional[float]
    coc_return_percentage: Optional[float] = Field(
        ..., description="Cash-on-Cash Return Percentage"
    )
    """
    Cash-on-Cash Return Percentage
    """

    down_payment_percentage: Optional[float]
    # TODO: should this also have a foreign key reference?
    exchange_rate: Optional[float]
    interest_rate: Optional[float]
    loan_term_years: Optional[float] = Field(
        ..., description="NOTE: Mapped as a ``float`` to leave room for partial years."
    )
    """
    NOTE: Mapped as a ``float`` to leave room for partial years.
    """

    monthly_expenses_cop: Optional[float]
    monthly_expenses_usd: Optional[float]
    payback_years: Optional[float] = Field(
        ..., description="NOTE: Mapped as a ``float`` to leave room for partial years."
    )
    """
    NOTE: Mapped as a ``float`` to leave room for partial years.
    """
