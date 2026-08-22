from __future__ import annotations

from models.listing.entity import ListingEntity
from models.market.entity import MarketEntity, MarketWithFinancialReportEntity
from utils.pydantic_helpers import BaseResponseModel


class MarketsListResponse(BaseResponseModel):
    data: list[MarketWithFinancialReportEntity]


class MarketOverviewData(BaseResponseModel):
    market: MarketEntity
    listings: list[ListingEntity]


class MarketOverviewResponse(BaseResponseModel):
    data: MarketOverviewData
