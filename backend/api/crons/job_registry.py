from __future__ import annotations

import asyncio

from api.app.main import crons
from api.crons.handlers import (
    handle_exchange_rate,
    handle_listings_by_market,
    handle_markets_summaries,
)


@crons.cron(
    "0 5 * * 1,3,5", name="ingest_markets_summaries", tags=["data_ingestion"]
)  # Every Monday, Wednesday, and Friday at 5am UTC (1am EST)
async def run_ingest_markets_summaries():
    return await asyncio.to_thread(handle_markets_summaries)


@crons.cron(
    "0 6 * * 1,3,5", name="ingest_listings_by_market", tags=["data_ingestion"]
)  # Every Monday, Wednesday, and Friday at 6am UTC (2am EST)
async def run_ingest_listings_by_market():
    return await asyncio.to_thread(handle_listings_by_market)


@crons.cron(
    "0 6 * * 1,3,5", name="ingest_exchange_rate", tags=["data_ingestion"]
)  # Every Monday, Wednesday, and Friday at 6am UTC (2am EST)
async def run_ingest_exchange_rate():
    return await asyncio.to_thread(handle_exchange_rate)
