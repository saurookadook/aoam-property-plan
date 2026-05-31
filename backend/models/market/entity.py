from __future__ import annotations

from datetime import datetime
from typing import Optional

from models.base.entity import BaseEntityModel
from models.mixins import TimestampsEntityMixin


class MarketEntity(BaseEntityModel, TimestampsEntityMixin):
    adr_usd: float
    annual_revenue_usd: float
    city: str
    country: str
    last_updated: datetime
    listing_count: float
    neighborhood: Optional[str]
    occupancy_rate: float
    peak_months: Optional[list[str]]
    region: str
