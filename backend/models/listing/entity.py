from __future__ import annotations

from decimal import Decimal
from typing import Any, Optional, Sequence
from uuid import UUID

from pydantic import Field, field_validator, model_validator

from models.base.entity import BaseEntityModel
from models.listing.db import ListingDB
from models.listing_financial_report.entity import ListingFinancialReportEntity
from models.mixins import TimestampsEntityMixin


class ListingEntity(BaseEntityModel, TimestampsEntityMixin):
    airroi_id: int
    amenities: list[str] = Field(default_factory=list)
    baths: Optional[float] = None
    beds: Optional[int] = None
    bedrooms: int
    cover_photo_url: Optional[str] = None
    description: Optional[str] = None
    latitude: float
    location: str
    longitude: float
    market_id: Optional[UUID] = None
    name: Optional[str] = None
    photo_urls: list[str] = Field(default_factory=list)
    property_type: str
    source_url: Optional[str] = None

    listing_financial_reports: list[ListingFinancialReportEntity] = Field(
        default_factory=list
    )

    @field_validator("location", mode="before")
    @classmethod
    def parse_location(cls, data_val: Sequence[Decimal] | str | Any) -> str:
        if isinstance(data_val, str):
            return data_val
        try:
            return f"POINT({float(data_val[1])} {float(data_val[0])})"
        except (TypeError, ValueError, IndexError) as exc:
            raise ValueError(
                "'location' must be a 'WKT POINT' string like `'POINT(lng lat)'` or a 2-item sequence `(lat, lon)`"
            ) from exc

    @model_validator(mode="before")
    @classmethod
    def validate_listing_financial_reports(
        cls, data: ListingDB | dict[str, Any]
    ) -> dict[str, Any]:
        if isinstance(data, ListingDB):
            input_data = dict(data.__dict__)
            input_data.pop("_sa_instance_state", None)
            input_data["listing_financial_reports"] = data.listing_financial_reports
        else:
            input_data = data

        if not isinstance(input_data.get("location"), str):
            # NOTE: WKT POINT order is `(longitude latitude)`
            input_data["location"] = (
                f"POINT({input_data['longitude']} {input_data['latitude']})"
            )

        return input_data


class NewestListingEntity(BaseEntityModel, TimestampsEntityMixin):
    cover_photo_url: Optional[str] = None
    market_id: UUID
    name: str
