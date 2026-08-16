from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, status

from api.dependencies.db_session import API_DB_SessionDependency
from api.models.property import PropertyCreateRequest, PropertyResponse
from models.property.facade import PropertyFacade
from services import property_source
from services.exceptions import FetchError, ScrapeError, UnsupportedSource
from services.exchange_rate import convert_cop_to_usd, resolve_cop_per_usd
from utils.logging.init import init_logging

logger = init_logging(__file__)

properties_router = APIRouter(prefix="/api")


@properties_router.post(
    "/properties",
    response_model=PropertyResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_property(
    request_body: PropertyCreateRequest, api_db_session: API_DB_SessionDependency
):
    """
    Adds a candidate property, either by scraping ``source_url`` or from a full
    manual body.

    Re-submitting a ``source_url`` already on file updates that record in place
    rather than inserting a second one - see ``properties_source_url_key``.
    """
    if request_body.is_manual:
        property_payload = request_body.manual_payload()
    else:
        property_payload = _scrape(request_body.source_url)

    property_payload.update(request_body.overrides())
    property_payload["source_url"] = request_body.source_url
    property_payload["purchase_price_usd"] = _resolve_price_usd(
        property_payload.get("purchase_price_cop"), api_db_session
    )

    try:
        property_record = PropertyFacade(db_session=api_db_session).create_or_update(
            payload=property_payload
        )
    except Exception as e:
        error_detail = "Error saving property"
        logger.error(f"{error_detail}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_detail,
        ) from e

    return {"data": property_record}


def _scrape(source_url: str) -> dict[str, Any]:
    # NOTE: ``UnsupportedSource`` and ``FetchError`` both subclass ``ScrapeError``,
    # so they have to be caught before it.
    try:
        return property_source.scrape(source_url)
    except UnsupportedSource as e:
        logger.warning(f"Unsupported listing source '{source_url}': {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except FetchError as e:
        logger.error(f"Could not reach listing page '{source_url}': {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Could not retrieve listing page at '{source_url}'",
        ) from e
    except ScrapeError as e:
        logger.error(f"Could not parse listing page '{source_url}': {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(e),
        ) from e


def _resolve_price_usd(
    purchase_price_cop: Any, api_db_session: API_DB_SessionDependency
) -> float | None:
    """
    Converts the COP price using our own rate.

    Deliberately never uses Finca Raiz's ``price_amount_usd``: it is computed at a
    materially different rate (~3216 vs ~4150 COP/USD), which would put a property
    on a different footing to every other USD figure in the system.
    """
    if purchase_price_cop is None:
        return None

    exchange_rate = resolve_cop_per_usd(api_db_session)

    if exchange_rate is None:
        logger.warning(
            "No exchange rate available - storing property without a USD price"
        )
        return None

    return convert_cop_to_usd(purchase_price_cop, exchange_rate.cop_per_usd)
