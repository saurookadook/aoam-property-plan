from __future__ import annotations

from datetime import datetime
from uuid import UUID

from models.base.entity import BaseEntityModel
from models.mixins import TimestampsEntityMixin


class PropertyFinancialReportEntity(BaseEntityModel, TimestampsEntityMixin):
    property_id: UUID
    annual_net_income_usd: float
    annual_revenue_usd: float
    calculated_at: datetime
    cash_invested_usd: float
    coc_return_percentage: float
    """
    Cash-on-Cash Return Percentage
    """

    down_payment_percentage: float
    exchange_rate: float
    """
    TODO: should this also have a foreign key reference?
    """

    interest_rate: float
    loan_term_years: float
    """
    NOTE: Mapped as a ``float`` to leave room for partial years.
    """

    monthly_expenses_usd: float
    payback_years: float
    """
    NOTE: Mapped as a ``float`` to leave room for partial years.
    """
