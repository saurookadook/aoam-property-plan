from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from models.base.entity import BaseEntityModel
from models.mixins import TimestampsEntityMixin


class MarketFinancialReportEntity(BaseEntityModel, TimestampsEntityMixin):
    market_id: UUID
    adr_cop: float
    adr_usd: Optional[float] = None
    annual_revenue_cop: float
    annual_revenue_usd: Optional[float] = None
    last_updated: datetime
    listing_count: float
    monthly_revenue_distribution: Optional[list[float]] = None
    occupancy_rate: float
    peak_months: Optional[list[str]]
