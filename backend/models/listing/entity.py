from __future__ import annotations

from decimal import Decimal
from typing import Any, Optional, Sequence
from uuid import UUID

from pydantic import field_validator

from models.base.entity import BaseEntityModel
from models.mixins import TimestampsEntityMixin


class ListingEntity(BaseEntityModel, TimestampsEntityMixin):
    airroi_id: int
    bedrooms: int
    cover_photo_url: Optional[str]
    latitude: float
    location: str
    longitude: float
    market_id: Optional[UUID]
    property_type: str
    source_url: Optional[str]

    @field_validator("location", mode="before")
    @classmethod
    def parse_location(cls, data_val: Sequence[Decimal] | str | Any) -> str:
        if isinstance(data_val, str):
            return str(data_val)
        try:
            return f"POINT({float(data_val[1])} {float(data_val[0])})"
        except:
            raise TypeError(
                f"Argumnt 'data_val' must be of type 'Sequence[Decimal] | str | Any'. Received: {data_val} '{type(data_val)}'"
            )
