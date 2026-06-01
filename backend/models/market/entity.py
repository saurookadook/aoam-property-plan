from __future__ import annotations

from typing import Optional

from models.base.entity import BaseEntityModel
from models.mixins import TimestampsEntityMixin


class MarketEntity(BaseEntityModel, TimestampsEntityMixin):
    country: str
    district: Optional[str]
    locality: str
    region: str
