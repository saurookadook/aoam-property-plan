#!/usr/bin/env python3
"""
Seeds ``properties`` from real Finca Raiz listings, one group per market.

Beside ``seed_markets.py`` and for the same reason: the budget indicator on the
market overview is a median of the scraped purchase prices in a market, and it is
hidden below three properties. A clean database therefore shows "Not enough price
data (0)" on every market until something puts real listings in the table, and
there is no ingest job that does - ``properties`` is only ever written by
``POST /api/properties``, one URL at a time, by hand.

Each entry carries both a ``source_url`` and the payload that URL parsed to when
it was captured. The URL is preferred, because a re-scrape picks up a price
change; the capture is the fallback, because Colombian listings are delisted
within months and a seed script that breaks when a house sells is not much of a
seed script. Which one was used is logged either way.

Run after ``seed_markets.py`` and ``seed_listings.py``: ``market_id`` is resolved
from the nearest market centroid, and a centroid is an average over ingested
``listings``. Run before them and every property is stored with a null market,
which is not wrong - just useless to the indicator.
"""

from __future__ import annotations

import gzip
import json
import sys
import traceback
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from api.routes.handlers.properties import resolve_market_id
from db.db_session_manager import DBSessionManager
from models.market.db import MarketDB
from models.property.facade import PropertyFacade
from services import property_source
from services.exceptions import ScrapeError
from services.exchange_rate import convert_cop_to_usd, resolve_cop_per_usd
from utils.filesystem import get_module_root
from utils.logging.init import init_logging

logger = init_logging(__file__)

SEED_FILE = "finca_raiz_listings.json.gz"


def seed_db_with_properties():
    local_db_session = DBSessionManager().scoped_session()

    seed_file = (
        get_module_root(__file__)
        / "scripts"
        / "db"
        / "seeding"
        / "seed_data"
        / "properties"
        / SEED_FILE
    )

    with gzip.open(
        seed_file, "rt", encoding="utf-8"
    ) as gz_text:
        document = json.load(gz_text)
    # with open(seed_file, "r") as f:

    logger.info(
        f"Seeding properties from '{seed_file.name}', captured "
        f"{document.get('captured_at')}"
    )

    property_facade = PropertyFacade(db_session=local_db_session)
    exchange_rate = resolve_cop_per_usd(local_db_session)

    if exchange_rate is None:
        logger.warning(
            "No exchange rate available - properties will be stored without a "
            "USD price. Run 'manual_run exchange_rate' and re-run this script."
        )

    failed_exceptions: list[str] = []
    seeded_count = 0

    for market_entry in document.get("markets", []):
        market_details = market_entry.get("market", {})
        locality = market_details.get("locality")
        source_entries = market_entry.get("properties", [])

        if not source_entries:
            logger.warning(
                f"No listings captured for market '{locality}' - its budget "
                f"indicator will stay empty. Add at least three to "
                f"'{SEED_FILE}'."
            )
            continue

        expected_market_id = _market_id_for(local_db_session, market_details)

        for source_entry in source_entries:
            source_url = source_entry["source_url"]

            try:
                payload = _payload_for(source_entry)
                payload["source_url"] = source_url
                payload["market_id"] = resolve_market_id(
                    local_db_session,
                    latitude=payload["latitude"],
                    longitude=payload["longitude"],
                )
                # Never Finca Raiz's own USD figure, for the same reason
                # ``POST /api/properties`` never uses it: the site converts at a
                # materially different rate.
                payload["purchase_price_usd"] = convert_cop_to_usd(
                    payload.get("purchase_price_cop"),
                    exchange_rate.cop_per_usd if exchange_rate else None,
                )

                # A mismatch is worth saying out loud rather than correcting.
                # The file's grouping is how a human filed the listing; the
                # resolved id is what the coordinates say, and it is the one
                # stored. They disagreeing means either the centroid has moved
                # with an ingest or the listing was filed under the wrong market.
                if payload["market_id"] is None:
                    logger.warning(
                        f"'{source_url}' resolved to no market - either "
                        f"'{locality}' has no ingested listings yet, or the "
                        f"property sits outside every market's radius"
                    )
                elif (
                    expected_market_id is not None
                    and payload["market_id"] != expected_market_id
                ):
                    logger.warning(
                        f"'{source_url}' is filed under '{locality}' but its "
                        f"coordinates resolve to market "
                        f"'{payload['market_id']}' - storing the resolved one"
                    )

                property_record = property_facade.create_or_update(payload=payload)
                local_db_session.commit()
                seeded_count += 1
                logger.info(
                    f"Seeded property with id='{property_record.id}' "
                    f"(locality='{locality}'  |  "
                    f"price_cop={property_record.purchase_price_cop})"
                )
            except Exception as e:
                local_db_session.rollback()
                logger.error(
                    f"Error seeding property from '{source_url}': {e}",
                    exc_info=sys.exc_info(),
                )
                failed_exceptions.append(
                    "\n".join(traceback.format_tb(e.__traceback__))
                )
                continue

    logger.info(f"Seeded {seeded_count} properties.")

    if failed_exceptions:
        logger.error(f"Failed to seed {len(failed_exceptions)} properties.")
        for formatted_traceback in failed_exceptions:
            logger.error(formatted_traceback)

    local_db_session.close()
    DBSessionManager().scoped_session.remove()


def _payload_for(source_entry: dict[str, Any]) -> dict[str, Any]:
    """
    Scrapes the listing, falling back to the payload captured alongside it.

    Every ``ScrapeError`` is a fallback rather than a failure - a 404 for a sold
    house and a redesigned page that no longer parses are the same thing from
    here, and the capture is the answer to both.
    """
    source_url = source_entry["source_url"]

    try:
        return property_source.scrape(source_url)
    except ScrapeError as e:
        logger.warning(
            f"Could not scrape '{source_url}' ({e}) - falling back to the "
            f"payload captured with it"
        )

    captured = dict(source_entry["captured"])
    captured.setdefault("source_created_at", datetime.now(timezone.utc))
    captured.setdefault("status", "active")

    return captured


def _market_id_for(
    db_session: Session, market_details: dict[str, Any]
) -> Optional[UUID]:
    """
    The market the seed file files this group under, matched the same way
    ``seed_markets.py`` matches: the three-part tuple AirROI itself keys on.

    ``None`` when the market has not been seeded, which is not an error here -
    only a reason the cross-check below has nothing to compare against.
    """
    return db_session.execute(
        select(MarketDB.id).where(
            and_(
                MarketDB.locality == market_details.get("locality"),
                MarketDB.country == market_details.get("country"),
                MarketDB.region == market_details.get("region"),
            )
        )
    ).scalar_one_or_none()


if __name__ == "__main__":
    seed_db_with_properties()
