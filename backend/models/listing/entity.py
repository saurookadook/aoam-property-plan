from __future__ import annotations

from typing import Optional
from uuid import UUID

from models.base.entity import BaseEntityModel
from models.mixins import TimestampsEntityMixin


class ListingEntity(BaseEntityModel, TimestampsEntityMixin):
    adr_usd: float
    airroi_id: UUID
    annual_revenue_cop: float
    annual_revenue_usd: Optional[float]
    bedrooms: int
    latitude: float
    location: str
    longitude: float
    market_id: UUID | None
    occupancy_rate: float
    property_type: str
    source_url: str
