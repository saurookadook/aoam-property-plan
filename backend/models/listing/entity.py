from __future__ import annotations

from typing import Optional
from uuid import UUID

from models.base.entity import BaseEntityModel
from models.mixins import TimestampsEntityMixin


class ListingEntity(BaseEntityModel, TimestampsEntityMixin):
    airroi_id: int
    adr_cop: float
    adr_usd: Optional[float]
    annual_revenue_cop: float
    annual_revenue_usd: Optional[float]
    bedrooms: int
    latitude: float
    location: str
    longitude: float
    market_id: Optional[UUID]
    occupancy_rate: float
    property_type: str
    source_url: str
