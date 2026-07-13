from __future__ import annotations

from models.listing.entity import ListingEntity
from utils.pydantic_helpers import BaseResponseModel


class ListingsListResponse(BaseResponseModel):
    data: list[ListingEntity]


class ListingResponse(BaseResponseModel):
    data: ListingEntity
