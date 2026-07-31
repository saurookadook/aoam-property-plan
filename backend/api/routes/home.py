from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from api.dependencies.db_session import API_DB_SessionDependency
from api.models.home import HighestEarningListingsResponse, NewestListingsResponse
from api.routes.handlers.home import get_highest_earners
from models.listing.facade import ListingFacade
from utils.logging.init import init_logging

logger = init_logging(__file__)

listings_router = APIRouter(prefix="/api")


@listings_router.get(
    "/home/listings/newest",
    response_model=NewestListingsResponse,
)
def read_home_newest_listings(api_db_session: API_DB_SessionDependency):
    try:
        listings = ListingFacade(db_session=api_db_session).get_newest()
    except Exception as e:
        error_detail = "Error fetching newest listings"
        logger.error(f"{error_detail}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_detail,
        ) from e

    return {"data": listings}


@listings_router.get(
    "/home/listings/highest-earners",
    response_model=HighestEarningListingsResponse,
)
def read_home_highest_earners_listings(api_db_session: API_DB_SessionDependency):
    try:
        highest_earning_listings_summary = get_highest_earners(
            db_session=api_db_session
        )
    except Exception as e:
        error_detail = "Error fetching highest earning listings"
        logger.error(f"{error_detail}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_detail,
        ) from e

    return {"data": highest_earning_listings_summary}
