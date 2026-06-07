from __future__ import annotations

from typing import Optional
from uuid import UUID

from models.base.entity import BaseEntityModel
from models.mixins import TimestampsEntityMixin


class ListingEntity(BaseEntityModel, TimestampsEntityMixin):
    airroi_id: int
    bedrooms: int
    latitude: float
    location: str
    longitude: float
    market_id: Optional[UUID]
    property_type: str
    source_url: Optional[str]
