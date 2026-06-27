from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException, status

from api.dependencies.db_session import DBSessionDependency
from api.models.market import MarketOverviewResponse, MarketsListResponse
from db.db_session_manager import DBSessionManager
from models.listing.facade import ListingFacade
from models.market.facade import MarketFacade
from utils.logging.init import init_logging

logger = init_logging(__file__)

markets_router = APIRouter(prefix="/api")


@markets_router.get(
    "/markets",
    response_model=MarketsListResponse,
)
def read_markets_list(db_session_dep: Optional[DBSessionDependency] = None):
    markets = []

    try:
        db_session = DBSessionManager().scoped_session()

        markets = MarketFacade(db_session=db_session).get_all()
    except Exception as e:
        logger.error(f"Error fetching markets: {e}")

    return {"data": markets}


@markets_router.get(
    "/markets/{market_id}",
    response_model=MarketOverviewResponse,
)
def read_market_overview(
    market_id: str, db_session_dep: Optional[DBSessionDependency] = None
):
    market_overview_data = {}

    # NOTE: make this work? :']
    # db_session = yield db_session_dep
    db_session = DBSessionManager().scoped_session()
    market_facade = MarketFacade(db_session=db_session)

    try:
        market_overview_data["market"] = market_facade.get_one_by_id(market_id)
    except Exception as e:
        logger.error(f"Error fetching market overview: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching market overview",
        )

    listing_facade = ListingFacade(db_session=db_session)

    try:
        market_overview_data["listings"] = listing_facade.get_all_by_market_id(
            market_overview_data["market"].id
        )
    except Exception as e:
        logger.error(f"Error fetching market listings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching market listings",
        )

    return {"data": market_overview_data}
