from __future__ import annotations

from typing import Annotated, Literal, Optional

from fastapi import APIRouter, HTTPException, Query, status

from api.dependencies.db_session import API_DB_SessionDependency
from api.models.market import MarketOverviewResponse, MarketsListResponse
from models.listing.facade import ListingFacade
from models.market.facade import MarketFacade
from utils.logging.init import init_logging

logger = init_logging(__file__)

markets_router = APIRouter(prefix="/api")

MAX_MARKET_LISTINGS = 200


@markets_router.get(
    "/markets",
    response_model=MarketsListResponse,
)
def read_markets_list(api_db_session: API_DB_SessionDependency):
    """
    The whole roster, each market carrying its latest figures and its centroid.

    ``financial_report`` and the coordinates are nullable: a seeded market with
    no summary yet, or one with nothing ingested, is still listed.
    """
    markets = []

    with api_db_session as db_session:
        try:
            markets = MarketFacade(db_session=db_session).get_all_with_latest_reports()
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
def read_market_overview(
    market_id: str,
    api_db_session: API_DB_SessionDependency,
    bedrooms: Annotated[
        Optional[int],
        Query(ge=0, description="Only listings with exactly this many bedrooms."),
    ] = None,
    property_type: Annotated[
        Optional[str],
        Query(description="Only listings of this AirROI property type."),
    ] = None,
    sort: Annotated[
        Optional[Literal["revenue", "occupancy"]],
        Query(
            description=(
                "Order listings by their latest financial report, highest first."
                " Defaults to `airroi_id` ascending."
            )
        ),
    ] = None,
    limit: Annotated[
        Optional[int],
        Query(
            ge=1,
            le=MAX_MARKET_LISTINGS,
            description="Maximum listings to return.",
        ),
    ] = None,
):
    """
    A market and its listings, with the listings' financial reports attached.

    All four query params are optional and are applied in the query rather than
    afterwards, so ``limit`` caps what the database returns.

    NOTE: omitting every param no longer reproduces this route's historical
    ordering, because it had none - listings came back in whatever order
    Postgres chose. They are now ordered by ``airroi_id`` ascending.
    """
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

        listing_facade = ListingFacade(db_session=db_session)

        try:
            market_overview_data["listings"] = listing_facade.get_all_by_market_id(
                market_overview_data["market"].id,
                bedrooms=bedrooms,
                property_type=property_type,
                sort=sort,
                limit=limit,
                include_financial_reports=True,
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
