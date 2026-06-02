from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from models.base.entity import BaseEntityModel
from models.mixins import TimestampsEntityMixin


class MarketFinancialReportEntity(BaseEntityModel, TimestampsEntityMixin):
    market_id: UUID
    adr_usd: float
    annual_revenue_usd: float
    last_updated: datetime
    listing_count: float
    occupancy_rate: float
    peak_months: Optional[list[str]]
