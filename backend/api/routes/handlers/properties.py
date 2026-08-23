from __future__ import annotations

import logging
from typing import Any, Callable, Optional, TypeVar
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.market.facade import MarketFacade
from models.property.facade import PropertyFacade
from models.property_financial_report.entity import PropertyFinancialReportEntity
from services.calculations import analyze, sensitivity
from services.exceptions import (
    AirROIError,
)
from services.geo import haversine_km
from services.property_analysis import scenario_from_report

T = TypeVar("T")

MARKET_MATCH_RADIUS_KM = 50.0
"""
How far a property may sit from a market's centroid and still be filed under it.

Nearest-centroid on its own would file every property in Colombia against some
market, and the budget indicator is a median of the properties in one - a
Medellin apartment landing in the Salento bucket does not make that median
wrong-looking, it makes it wrong. 50km is wider than any single locality's
listing footprint and far narrower than the gaps between the roster's markets
(Calima to Pance is roughly 65km, Bogota to Salento roughly 200km), so a property
on the edge of a market still matches and one in a city we do not track matches
nothing.
"""


def run_analysis(
    operation: Callable[[], T], *, error_detail: str, logger: logging.Logger
) -> T:
    """
    Maps what ``services.property_analysis`` raises onto status codes.

    ``AirROIError`` is a 502 rather than a 500: the request was fine and our side
    worked, an upstream we depend on did not. ``ValueError`` is a 422 because the
    service only raises it when the stored property cannot supply an input the
    analysis needs - a missing bath count or purchase price - which the caller can
    fix and retry.
    """
    try:
        return operation()
    except PropertyFacade.NoResultFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found",
        ) from e
    except AirROIError as e:
        logger.error(f"{error_detail} - AirROI call failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Could not retrieve revenue data from AirROI",
        ) from e
    except ValueError as e:
        logger.warning(f"{error_detail}: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(e),
        ) from e
    except Exception as e:
        logger.error(f"{error_detail}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_detail,
        ) from e


def build_analysis_data(report: PropertyFinancialReportEntity) -> dict[str, Any]:
    """
    Wraps a stored report in the two figures the analysis panel also needs.

    Both are rebuilt from the report through ``scenario_from_report``, so a
    freshly written report and one read back a month later are explained by
    exactly the same arithmetic - there is no second code path for the read side
    to drift down.
    """
    scenario = scenario_from_report(report)

    return {
        "report": report,
        "expenses": analyze(scenario).monthly_expenses,
        "sensitivity": sensitivity(scenario),
    }


def resolve_market_id(
    db_session: Session, *, latitude: float, longitude: float
) -> Optional[UUID]:
    """
    Which market a property belongs to, decided by coordinates.

    ``markets.locality`` is AirROI's name for a place and ``properties.city`` is
    whatever Finca Raiz printed on the page, so the two cannot be joined on text:
    a cabin in Pance is filed under ``city='Cali'`` and would match no market at
    all. Coordinates are the only thing both sides agree on.

    Nearest centroid wins, within ``MARKET_MATCH_RADIUS_KM``. Returns ``None``
    when nothing is close enough, or when no market has ingested listings yet -
    an unmatched property is still a property worth storing, it just cannot
    contribute to a market's budget indicator.

    Distance is measured with ``services.geo.haversine_km`` rather than in
    Postgres for the same reason a comp's distance is: this runs once per created
    property against a handful of centroids, and ``ST_Distance`` would mean a
    round trip to learn something a single subtraction already answers.
    """
    centroids = MarketFacade(db_session=db_session).get_all_centroids()

    if not centroids:
        return None

    nearest = min(
        centroids,
        key=lambda centroid: haversine_km(
            latitude, longitude, centroid.latitude, centroid.longitude
        ),
    )
    distance_km = haversine_km(latitude, longitude, nearest.latitude, nearest.longitude)

    if distance_km > MARKET_MATCH_RADIUS_KM:
        return None

    return nearest.market_id
