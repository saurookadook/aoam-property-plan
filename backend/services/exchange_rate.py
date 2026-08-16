from __future__ import annotations

import logging
from datetime import date, datetime, timezone
from typing import Optional, cast

import requests
from sqlalchemy.orm import Session

from models.exchange_rate.entity import ExchangeRateEntity
from models.exchange_rate.facade import ExchangeRateFacade
from utils.logging.extended_logger import ExtendedLogger

logger = cast(ExtendedLogger, logging.getLogger(__name__))

FRANKFURTER_RATES_URL = "https://api.frankfurter.dev/v2/rates"
REQUEST_TIMEOUT = 30


def resolve_cop_per_usd(
    db_session: Session, *, on_date: Optional[date] = None
) -> Optional[ExchangeRateEntity]:
    """
    Returns the rate to convert a COP price to USD - the most recent one recorded
    on or before ``on_date``, fetching and storing one if none exists yet.

    The cold-start path matters: ``handle_exchange_rate`` only writes a rate row
    for a date that already has a listing financial report, so a fresh database
    can legitimately hold no rates at all. Without the fallback, the first
    property added to a new environment would get no USD price.
    """
    target_date = on_date or datetime.now(timezone.utc).date()
    exchange_rate_facade = ExchangeRateFacade(db_session=db_session)

    exchange_rate = exchange_rate_facade.get_latest_on_or_before(target_date)
    if exchange_rate is not None:
        return exchange_rate

    logger.info(
        f"No exchange rate on or before '{target_date}' - fetching one from "
        f"frankfurter"
    )

    return _fetch_and_store(exchange_rate_facade, target_date)


def convert_cop_to_usd(
    amount_cop: Optional[float], cop_per_usd: Optional[float]
) -> Optional[float]:
    """Converts COP to USD, returning ``None`` when either input is unusable."""
    if amount_cop is None or not cop_per_usd:
        return None

    return float(amount_cop) / float(cop_per_usd)


def _fetch_and_store(
    exchange_rate_facade: ExchangeRateFacade, target_date: date
) -> Optional[ExchangeRateEntity]:
    try:
        response = requests.get(
            f"{FRANKFURTER_RATES_URL}?base=USD&quotes=COP&date={target_date}",
            headers={"Content-Type": "application/json"},
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        result = response.json()
    except (ValueError, requests.RequestException) as exc:
        logger.error(f"Error fetching exchange rate for date='{target_date}': {exc}")
        return None

    if isinstance(result, dict):
        result = [result]

    for rate_record in result or []:
        try:
            return exchange_rate_facade.create_or_update(
                payload={
                    "record_date": rate_record["date"],
                    "cop_per_usd": rate_record["rate"],
                }
            )
        except (KeyError, TypeError) as exc:
            logger.error(
                f"Malformed exchange rate record for date='{target_date}': {exc}"
            )
            continue

    return None
