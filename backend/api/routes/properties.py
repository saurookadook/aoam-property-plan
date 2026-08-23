from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, HTTPException, status

from api.dependencies.db_session import API_DB_SessionDependency
from api.models.property import (
    PropertiesListResponse,
    PropertyCreateRequest,
    PropertyResponse,
)
from api.models.property_analysis import (
    PropertyAnalysisReportResponse,
    PropertyAnalysisResponse,
    PropertyAnalyzeRequest,
    PropertyCompsResponse,
)
from api.routes.handlers.properties import (
    build_analysis_data,
    resolve_market_id,
    run_analysis,
)
from models.property.facade import PropertyFacade
from models.property_comp.facade import PropertyCompFacade
from models.property_financial_report.facade import PropertyFinancialReportFacade
from services import property_analysis, property_source
from services.exceptions import (
    FetchError,
    ScrapeError,
    UnsupportedSource,
)
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

    TODO: move the body of this function to a handler in ``handlers/properties.py``
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
    # Resolved here rather than on read so that a property's market is a fact
    # about the record, settled by the coordinates it was created with. Nearest
    # centroid moves as listings are ingested; re-deriving it on every read would
    # silently reassign stored properties between markets.
    property_payload["market_id"] = resolve_market_id(
        api_db_session,
        latitude=property_payload["latitude"],
        longitude=property_payload["longitude"],
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


@properties_router.get(
    "/properties",
    response_model=PropertiesListResponse,
)
def read_properties_list(api_db_session: API_DB_SessionDependency):
    """Every stored property, most recently added first."""
    try:
        properties = PropertyFacade(db_session=api_db_session).get_all()
    except Exception as e:
        error_detail = "Error fetching properties"
        logger.error(f"{error_detail}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_detail,
        ) from e

    return {"data": properties}


@properties_router.get(
    "/properties/{property_id}",
    response_model=PropertyResponse,
)
def read_property(property_id: str, api_db_session: API_DB_SessionDependency):
    """One stored property, as it was saved. Makes no AirROI call."""
    try:
        property_record = PropertyFacade(db_session=api_db_session).get_one_by_id(
            property_id
        )
    except PropertyFacade.NoResultFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found",
        ) from e
    except Exception as e:
        error_detail = "Error fetching property"
        logger.error(f"{error_detail}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_detail,
        ) from e

    return {"data": property_record}


@properties_router.get(
    "/properties/{property_id}/report",
    response_model=PropertyAnalysisReportResponse,
)
def read_property_report(property_id: str, api_db_session: API_DB_SessionDependency):
    """
    The latest stored analysis, rebuilt into the full envelope. No AirROI call.

    This is what a deep-dive page load reads. ``POST /analyze`` spends an API
    call and rewrites the comp set every time, so reloading through it would
    charge for every refocus and every StrictMode double-mount.

    ``{"data": null}`` with a 200 for a property that has never been analysed -
    the same answer shape ``/comps/cached`` gives, for the same reason.
    """
    try:
        PropertyFacade(db_session=api_db_session).get_one_by_id(property_id)
        report = PropertyFinancialReportFacade(
            db_session=api_db_session
        ).get_latest_by_property_id(property_id)
    except PropertyFacade.NoResultFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found",
        ) from e
    except Exception as e:
        error_detail = "Error fetching property report"
        logger.error(f"{error_detail}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_detail,
        ) from e

    if report is None:
        return {"data": None}

    return {"data": build_analysis_data(report)}


@properties_router.post(
    "/properties/{property_id}/analyze",
    response_model=PropertyAnalysisResponse,
    status_code=status.HTTP_201_CREATED,
)
def analyze_property(
    property_id: str,
    api_db_session: API_DB_SessionDependency,
    request_body: Optional[PropertyAnalyzeRequest] = None,
):
    """
    Analyses a property against AirROI's revenue data and stores the result.

    Every call writes a new report rather than replacing the last one, so a
    property keeps the history of what it looked like under different assumptions.
    The body is optional - omitting it analyses under the Colombia defaults.

    NOTE: ``data`` is the full analysis envelope - report, monthly expense
    breakdown and sensitivity sweep - not the report on its own.
    """
    report = run_analysis(
        lambda: property_analysis.analyze_property(
            api_db_session,
            property_id=property_id,
            overrides=request_body.overrides() if request_body else {},
        ),
        error_detail="Error analysing property",
        logger=logger,
    )

    return {"data": build_analysis_data(report)}


@properties_router.get(
    "/properties/{property_id}/comps",
    response_model=PropertyCompsResponse,
)
def read_property_comps(property_id: str, api_db_session: API_DB_SessionDependency):
    """
    Today's comparables for a property, refreshed from AirROI on every call.

    Spends an API call each time and rewrites the stored comp set. Use
    ``/comps/cached`` to read the set an analysis was actually built on.
    """
    comps = run_analysis(
        lambda: property_analysis.refresh_comps(
            api_db_session, property_id=property_id
        ),
        error_detail="Error refreshing property comps",
        logger=logger,
    )

    return {"data": comps}


@properties_router.get(
    "/properties/{property_id}/comps/cached",
    response_model=PropertyCompsResponse,
)
def read_cached_property_comps(
    property_id: str, api_db_session: API_DB_SessionDependency
):
    """
    The stored comp set, nearest first. Makes no AirROI call.

    Returns an empty list for a property that has never been analysed - that is
    an answer, not an error, so it is a 200 rather than a 404.
    """
    try:
        PropertyFacade(db_session=api_db_session).get_one_by_id(property_id)
        comps = PropertyCompFacade(db_session=api_db_session).get_all_by_property_id(
            property_id
        )
    except PropertyFacade.NoResultFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found",
        ) from e
    except Exception as e:
        error_detail = "Error fetching property comps"
        logger.error(f"{error_detail}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_detail,
        ) from e

    return {"data": comps}


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
