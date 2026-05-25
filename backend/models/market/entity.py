from __future__ import annotations

from models.mixins import TimestampsEntityMixin
from utils.pydantic_helpers import BaseEntityModel


class MarketEntity(BaseEntityModel, TimestampsEntityMixin):
    adr_usd: float
    annual_revenue_usd: float
    city: str
    country: str
    listing_count: int
    neighborhood: str
    occupancy_rate: float
    peak_months: list[str]
