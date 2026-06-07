from __future__ import annotations

from datetime import datetime
from typing import Optional

from models.base.entity import BaseEntityModel
from models.mixins import TimestampsEntityMixin


class PropertyEntity(BaseEntityModel, TimestampsEntityMixin):
    address: str
    bedrooms: int
    city: str
    country: str
    latitude: float
    longitude: float
    neighborhood: str
    notes: Optional[str]
    postal_code: str
    property_type: str
    purchase_price_cop: float
    purchase_price_usd: Optional[float] = None
    source_created_at: datetime
    source_url: str
    state: str
