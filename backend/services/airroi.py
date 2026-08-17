"""
The one place AirROI is spoken to.

Before this module the API was reached by two inline ``requests.post`` calls in
``api/crons/handlers.py``, each carrying its own copy of the header dict and
``timeout=30``. Step 6 needs two more endpoints and a route that calls one of
them, so the duplication is collected here and the handlers go back to being
purely about the database.

Everything is requested in AirROI's ``native`` currency, which for Colombia is
COP - the captures in ``_research/`` all come back ``"currency": "COP"``. USD
figures are ours to derive from ``services.exchange_rate``, never AirROI's, so
that one rate explains every ``_usd`` column in a report.

Each function returns the decoded body untouched. Reshaping a response into
columns is the caller's job; this module's only opinion is that a failed call
raises ``AirROIError`` rather than returning something falsy that a caller might
mistake for an empty result.
"""

from __future__ import annotations

import logging
from typing import Any, Callable, cast

import requests

from config.env_var_manager import EnvVarManager
from constants import AIRROI_BASE_URL
from models.market.entity import MarketEntity
from services.exceptions import AirROIError
from utils.logging.extended_logger import ExtendedLogger

logger = cast(ExtendedLogger, logging.getLogger(__name__))

_BASE_URL = AIRROI_BASE_URL
REQUEST_TIMEOUT = 30

# ``native`` leaves conversion to us. Asking AirROI for USD would mix its rate
# into figures the rest of the app converts with a rate off ``exchange_rates``.
CURRENCY = "native"

DEFAULT_PAGE_SIZE = 10
DEFAULT_RADIUS_KM = 10
DEFAULT_ROOM_TYPE = "entire_home"

# The market ingest deliberately ignores anything larger - a 6-bedroom finca is
# not a comparable for the properties this app is built to appraise.
MARKET_BEDROOMS_RANGE = [1, 3]
MARKET_SUMMARY_MONTHS = 12


def get_revenue_estimate(
    *,
    latitude: float,
    longitude: float,
    bedrooms: int,
    baths: float,
    guests: int,
) -> dict[str, Any]:
    """
    Returns AirROI's revenue estimate for a point, with its comp set inline.

    One call covers most of an analysis: ``revenue`` / ``average_daily_rate`` /
    ``occupancy``, the ``percentiles`` block behind them,
    ``monthly_revenue_distributions`` (twelve fractions summing to 1.0), and up
    to 25 ``comparable_listings`` shaped exactly like ``/listings/search/market``
    results.

    ``bedrooms``, ``baths`` and ``guests`` are all required by the endpoint, and
    a thin local pool makes it quietly stop honouring them - both Calima captures
    came back with the same single 5br/5.5ba/16-guest comp, for a 2br query and a
    3br query alike. Callers cannot tell that from the response and have to gate
    on the comp count themselves.

    No ``currency`` parameter is sent: the captures this was built against return
    ``"COP"`` without one, and guessing at an undocumented query parameter on a
    metered API is a worse bet than relying on the default we have evidence for.
    """
    return _get(
        "/calculator/estimate",
        {
            "lat": latitude,
            "lng": longitude,
            "bedrooms": bedrooms,
            "baths": baths,
            "guests": guests,
        },
    )


def get_comparables(
    *,
    latitude: float,
    longitude: float,
    bedrooms: int,
    baths: float,
    guests: int,
    radius: int = DEFAULT_RADIUS_KM,
    room_type: str = DEFAULT_ROOM_TYPE,
) -> dict[str, Any]:
    """
    Returns active listings near a point.

    A fallback, not the primary source: ``get_revenue_estimate`` already returns
    comps inline, so this is only worth a call when that set came back too thin
    to derive a median from. ``room_type`` filters on how the whole place is let
    ("entire_home"), not on the building type the execution plan describes.
    """
    return _get(
        "/listings/comparables",
        {
            "lat": latitude,
            "lng": longitude,
            "bedrooms": bedrooms,
            "baths": baths,
            "guests": guests,
            "radius": radius,
            "room_type": room_type,
        },
    )


def get_market_summary(market: MarketEntity) -> dict[str, Any]:
    """
    Returns a market's headline figures - ADR, occupancy, revenue, listing count.

    NOTE: it does not return ``peak_months``, despite the column of that name on
    ``market_financial_reports``. Seasonality only comes from
    ``monthly_revenue_distributions`` on ``/calculator/estimate``.
    """
    return _post(
        "/markets/summary",
        {
            "market": _market_body(market),
            "num_months": MARKET_SUMMARY_MONTHS,
            "currency": CURRENCY,
        },
    )


def search_listings_by_market(
    market: MarketEntity, *, offset: int, page_size: int = DEFAULT_PAGE_SIZE
) -> dict[str, Any]:
    """
    Returns one page of a market's listings, highest trailing-twelve-month
    revenue first.

    ``offset`` counts **records, not pages**. The nightly ingest used to pass the
    page index straight through, which is why ``…page-2`` in
    ``_research/listings/search-by-market/`` is ``…page-1`` shifted by a single
    listing - nine of its ten rows are duplicates. Callers page with
    ``offset=page_index * page_size``.
    """
    return _post(
        "/listings/search/market",
        {
            "market": _market_body(market),
            "filter": {
                "room_type": {"eq": DEFAULT_ROOM_TYPE},
                "bedrooms": {"range": MARKET_BEDROOMS_RANGE},
            },
            "sort": {"ttm_revenue": "desc"},
            "pagination": {"offset": offset, "page_size": page_size},
            "currency": CURRENCY,
        },
    )


def _headers() -> dict[str, str]:
    # Read per call rather than at import time so that the key is resolved
    # against whatever ``EnvVarManager`` holds when the request is actually made.
    return {
        "Content-Type": "application/json",
        "x-api-key": EnvVarManager().env_vars.airroi_api_key,
    }


def _market_body(market: MarketEntity) -> dict[str, str]:
    # ``district`` is deliberately left out: AirROI matches on the three-part
    # country/region/locality tuple, and sending a fourth key narrows nothing.
    return {
        "country": market.country,
        "region": market.region,
        "locality": market.locality,
    }


def _get(path: str, params: dict[str, Any]) -> dict[str, Any]:
    logger.info(f"GET {path} with params={params}")

    return _send(requests.get, path, params=params)


def _post(path: str, body: dict[str, Any]) -> dict[str, Any]:
    logger.info(f"POST {path}")

    return _send(requests.post, path, json=body)


def _send(
    method: Callable[..., requests.Response], path: str, **kwargs: Any
) -> dict[str, Any]:
    url = f"{_BASE_URL}{path}"

    try:
        response = method(url, headers=_headers(), timeout=REQUEST_TIMEOUT, **kwargs)
        response.raise_for_status()

        return response.json()
    # ``JSONDecodeError`` subclasses ``RequestException``, so it has to be caught
    # first or a malformed body is reported as a transport failure.
    except requests.exceptions.JSONDecodeError as exc:
        raise AirROIError(
            f"AirROI returned a malformed body for '{url}': {exc}"
        ) from exc
    except requests.RequestException as exc:
        raise AirROIError(f"AirROI request to '{url}' failed: {exc}") from exc
