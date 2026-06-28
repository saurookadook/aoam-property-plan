from __future__ import annotations

from models.listing.entity import ListingEntity
from models.market.entity import MarketEntity
from utils.pydantic_helpers import BaseResponseModel


class MarketsListResponse(BaseResponseModel):
    data: list[MarketEntity]


class MarketOverviewData(BaseResponseModel):
    market: MarketEntity
    listings: list[ListingEntity]


class MarketOverviewResponse(BaseResponseModel):
    data: MarketOverviewData
