from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import Field

from models.base.entity import BaseEntityModel
from models.mixins import TimestampsEntityMixin


class PropertyEntity(BaseEntityModel, TimestampsEntityMixin):
    address: str
    amenities: list[str] = Field(default_factory=list)
    baths: Optional[float] = None
    bedrooms: int
    city: str
    country: str
    description: Optional[str] = None
    guests: Optional[int] = None
    latitude: float
    longitude: float
    name: Optional[str] = None
    neighborhood: str
    notes: Optional[str]
    postal_code: Optional[str] = None
    property_type: str
    purchase_price_cop: Optional[float] = None
    purchase_price_usd: Optional[float] = None
    source_created_at: datetime
    source_url: str
    state: str
    status: str
