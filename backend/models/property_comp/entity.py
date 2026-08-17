from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from models.base.entity import BaseEntityModel
from models.mixins import TimestampsEntityMixin


class PropertyCompEntity(BaseEntityModel, TimestampsEntityMixin):
    adr_cop: Optional[float] = None
    captured_at: datetime
    distance_km: Optional[float] = None
    listing_id: UUID
    occupancy_rate: Optional[float] = None
    property_id: UUID
    ttm_revenue_cop: Optional[float] = None
    ttm_total_days: Optional[float] = None
