from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from api.dependencies.db_session import API_DB_SessionDependency
from api.models.listing import ListingResponse, ListingsListResponse
from models.listing.facade import ListingFacade
from utils.logging.init import init_logging

logger = init_logging(__file__)

listings_router = APIRouter(prefix="/api")


@listings_router.get(
    "/listings",
    response_model=ListingsListResponse,
)
def read_listings_list(api_db_session: API_DB_SessionDependency):
    try:
        listings = ListingFacade(db_session=api_db_session).get_all()
    except Exception as e:
        error_detail = "Error fetching listings"
        logger.error(f"{error_detail}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_detail,
        ) from e

    return {"data": listings}


@listings_router.get(
    "/listings/{listing_id}",
    response_model=ListingResponse,
)
def read_listing(listing_id: str, api_db_session: API_DB_SessionDependency):
    try:
        listing = ListingFacade(db_session=api_db_session).get_one_by_id(listing_id)
    except ListingFacade.NoResultFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Listing not found",
        ) from e
    except Exception as e:
        error_detail = "Error fetching listing"
        logger.error(f"{error_detail}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_detail,
        ) from e

    return {"data": listing}
