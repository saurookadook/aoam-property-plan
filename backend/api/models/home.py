from __future__ import annotations

from models.listing.entity import HighestEarningListingEntity, NewestListingEntity
from utils.pydantic_helpers import BaseResponseModel


class NewestListingsResponse(BaseResponseModel):
    data: list[NewestListingEntity]


class HighestEarningListingsResponse(BaseResponseModel):
    data: list[HighestEarningListingEntity]
