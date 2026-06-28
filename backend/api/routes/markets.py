from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.dependencies.db_session import API_DB_SessionDependency
from api.models.market import MarketOverviewResponse, MarketsListResponse
from models.listing.facade import ListingFacade
from models.market.facade import MarketFacade
from utils.logging.init import init_logging

logger = init_logging(__file__)

markets_router = APIRouter(prefix="/api")


@markets_router.get(
    "/markets",
    response_model=MarketsListResponse,
)
def read_markets_list(api_db_session: API_DB_SessionDependency):
    markets = []

    with api_db_session as db_session:
        try:
            markets = MarketFacade(db_session=db_session).get_all()
        except Exception as e:
            error_detail = "Error fetching markets"
            logger.error(f"{error_detail}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_detail,
            )

        return {"data": markets}


@markets_router.get(
    "/markets/{market_id}",
    response_model=MarketOverviewResponse,
)
def read_market_overview(market_id: str, api_db_session: API_DB_SessionDependency):
    market_overview_data = {}

    with api_db_session as db_session:
        market_facade = MarketFacade(db_session=db_session)

        try:
            market_overview_data["market"] = market_facade.get_one_by_id(market_id)
        except MarketFacade.NoResultFound as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Market not found",
            ) from e
        except Exception as e:
            error_detail = "Error fetching market overview"
            logger.error(f"{error_detail}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_detail,
            ) from e

        listing_facade = ListingFacade(db_session=api_db_session)

        try:
            market_overview_data["listings"] = listing_facade.get_all_by_market_id(
                market_overview_data["market"].id
            )
        except MarketFacade.NoResultFound as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Market not found",
            ) from e
        except Exception as e:
            error_detail = "Error fetching market listings"
            logger.error(f"{error_detail}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_detail,
            ) from e

        return {"data": market_overview_data}
