from __future__ import annotations

from decimal import Decimal
from typing import Any, Optional, Sequence
from uuid import UUID

from pydantic import field_validator

from sqlalchemy import func
from models.base.entity import BaseEntityModel
from models.listing.db import ListingDB
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
        if len(data_val) == 2:
            return f"POINT({float(data_val[0])} {float(data_val[1])})"
        elif isinstance(data_val, str):
            return data_val
        raise TypeError(
            f"Argumnt 'data_val' must be of type 'Sequence[Decimal] | str | Any'. Received: {data_val} '{type(data_val)}'"
        )
