from __future__ import annotations

from models.market.entity import MarketEntity
from utils.pydantic_helpers import BaseResponseModel


class MarketsListResponse(BaseResponseModel):
    data: list[MarketEntity]
