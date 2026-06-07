from __future__ import annotations

import asyncio

from api.app.main import crons
from api.crons.handlers import handle_markets_summaries


@crons.cron(
    "0 0 * * *", name="ingest_markets_summaries", tags=["data_ingestion"]
)  # Every day at midnight
async def run_ingest_markets_summaries():
    return await asyncio.to_thread(handle_markets_summaries)
