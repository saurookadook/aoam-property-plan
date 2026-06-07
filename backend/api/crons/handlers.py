from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import cast

import requests

from config.env_var_manager import EnvVarManager
from constants import AIRROI_BASE_URL
from db.db_session_manager import DBSessionManager
from models.market.facade import MarketFacade
from models.market_financial_report.facade import MarketFinancialReportFacade
from utils.logging.extended_logger import ExtendedLogger

logger = cast(ExtendedLogger, logging.getLogger(__name__))


def handle_markets_summaries():
    local_db_session = DBSessionManager().scoped_session()
    market_facade = MarketFacade(db_session=local_db_session)
    market_financial_report_facade = MarketFinancialReportFacade(
        db_session=local_db_session
    )

    all_markets = market_facade.get_all()
    env_vars = EnvVarManager().env_vars
    request_headers = {
        "Content-Type": "application/json",
        "x-api-key": env_vars.airroi_api_key,
    }

    for market in all_markets:
        logger.info(
            f"Handling market summary for market with id='{market.id}' "
            f"and locality='{market.locality}'"
        )
        try:
            response = requests.post(
                f"{AIRROI_BASE_URL}/markets/summary",
                headers=request_headers,
                json={
                    "market": {
                        "country": market.country,
                        "region": market.region,
                        "locality": market.locality,
                    },
                    "num_months": 12,
                    "currency": "native",
                },
                timeout=30,
            )
            response.raise_for_status()
            result = response.json()
        except (ValueError, requests.RequestException) as e:
            logger.error(
                f"Error fetching market summary for market with id='{market.id}' "
                f"and locality='{market.locality}': {e}"
            )
            continue

        try:
            market_financial_report_facade.create_or_update(
                payload={
                    "market_id": market.id,
                    "adr_cop": result["average_daily_rate"],
                    "annual_revenue_cop": float(result["revenue"]),
                    "last_updated": result.get(
                        "last_updated", datetime.now(timezone.utc)
                    ),
                    "listing_count": result["active_listings_count"],
                    "occupancy_rate": result["occupancy"],
                    "peak_months": result.get("peak_months", None),
                }
            )
            local_db_session.commit()
            logger.info(
                f"Finished handling market summary for market with id='{market.id}' "
                f"and locality='{market.locality}'"
            )
        except Exception as e:
            logger.error(
                f"Error creating/updating market financial report for market with id='{market.id}' "
                f"and locality='{market.locality}': {e}"
            )
            local_db_session.rollback()
            continue
    local_db_session.commit()
    local_db_session.close()
    DBSessionManager().scoped_session.remove()


if __name__ == "__main__":
    import argparse

    handler_ids = [
        "markets_summaries",
    ]

    parser = argparse.ArgumentParser(description="Manually run cron handlers")
    parser.add_argument(
        "handler_name",
        choices=handler_ids,
        help="Run the markets summaries handler",
    )

    args = parser.parse_args()
    if args.handler_name in handler_ids:
        handle_markets_summaries()
    else:
        logger.error(
            f"Invalid handler name: '{args.handler_name}'. Valid options are: {handler_ids}"
        )
