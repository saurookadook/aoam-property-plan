from __future__ import annotations

import logging
from typing import Callable, TypeVar

from fastapi import HTTPException, status

from models.property.facade import PropertyFacade
from services.exceptions import (
    AirROIError,
)

T = TypeVar("T")


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
