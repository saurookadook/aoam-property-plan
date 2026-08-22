from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from api.dependencies.db_session import API_DB_SessionDependency
from api.models.exchange_rate import ExchangeRateResponse
from services.exchange_rate import resolve_cop_per_usd
from utils.logging.init import init_logging

logger = init_logging(__file__)

exchange_rate_router = APIRouter(prefix="/api")


@exchange_rate_router.get(
    "/exchange-rate",
    response_model=ExchangeRateResponse,
)
def read_exchange_rate(api_db_session: API_DB_SessionDependency):
    """
    The COP-per-USD rate the whole UI converts with, and the date it is for.

    ``resolve_cop_per_usd`` handles the cold start: on a database with no rates
    yet - which is every fresh environment, since ``handle_exchange_rate`` only
    writes a rate for a date that already has a listing financial report - it
    fetches one and stores it.

    A missing rate is a **503, not a 200 with a null**. A currency toggle with
    nothing to convert by is a broken feature, not an empty result set, and
    returning null here would push that judgement onto every caller. The client
    should show the failure and keep displaying COP.
    """
    with api_db_session as db_session:
        try:
            exchange_rate = resolve_cop_per_usd(db_session)
        except Exception as e:
            error_detail = "Error fetching exchange rate"
            logger.error(f"{error_detail}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_detail,
            ) from e

        if exchange_rate is None:
            logger.warning("No exchange rate available to serve")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="No exchange rate available",
            )

        return {"data": exchange_rate}
