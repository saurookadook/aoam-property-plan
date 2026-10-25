from __future__ import annotations

import asyncio
import logging
from typing import cast

from api.app.main import crons
from api.crons.handlers import (
    handle_exchange_rate,
    handle_listings_by_market,
    handle_markets_peak_months,
    handle_markets_summaries,
)
from utils.logging.extended_logger import ExtendedLogger

logger = cast(ExtendedLogger, logging.getLogger(__name__))

disabled = True
"""
Disabled flag for cron jobs. When set to True, all cron jobs are disabled.
"""


@crons.cron(
    "0 5 * * 1,3,5", name="ingest_markets_summaries", tags=["data_ingestion"]
)  # Every Monday, Wednesday, and Friday at 5am UTC (1am EST)
async def run_ingest_markets_summaries():
    if disabled:
        logger.warning("[run_ingest_markets_summaries] Currently disabled... x_x")
        return
    return await asyncio.to_thread(handle_markets_summaries)


@crons.cron(
    "0 6 * * 1,3,5", name="ingest_listings_by_market", tags=["data_ingestion"]
)  # Every Monday, Wednesday, and Friday at 6am UTC (2am EST)
async def run_ingest_listings_by_market():
    if disabled:
        logger.warning("[run_ingest_listings_by_market] Currently disabled... x_x")
        return
    return await asyncio.to_thread(handle_listings_by_market)


@crons.cron(
    "0 6 * * 1,3,5", name="ingest_exchange_rate", tags=["data_ingestion"]
)  # Every Monday, Wednesday, and Friday at 6am UTC (2am EST)
async def run_ingest_exchange_rate():
    if disabled:
        logger.warning("[run_ingest_exchange_rate] Currently disabled... x_x")
        return
    return await asyncio.to_thread(handle_exchange_rate)


@crons.cron(
    "0 7 * * 1,3,5", name="ingest_markets_peak_months", tags=["data_ingestion"]
)  # Every Monday, Wednesday, and Friday at 7am UTC (3am EST)
# NOTE: an hour behind ``ingest_listings_by_market`` on purpose - the centroid it
# needs is computed from the listings that job ingests, and it updates the report
# ``ingest_markets_summaries`` writes two hours earlier.
async def run_ingest_markets_peak_months():
    if disabled:
        logger.warning("[run_ingest_markets_peak_months] Currently disabled... x_x")
        return
    return await asyncio.to_thread(handle_markets_peak_months)
