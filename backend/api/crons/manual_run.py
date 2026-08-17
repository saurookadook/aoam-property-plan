#!/usr/bin/env python3

from __future__ import annotations

from api.crons.handlers import (
    handle_exchange_rate,
    handle_listings_by_market,
    handle_markets_peak_months,
    handle_markets_summaries,
)
from utils.logging.init import init_logging

if __name__ == "__main__":
    import argparse

    logger = init_logging(__name__)

    handler_ids = [
        "exchange_rate",
        "listings_by_market",
        "markets_peak_months",
        "markets_summaries",
    ]

    parser = argparse.ArgumentParser(description="Manually run cron handlers")
    parser.add_argument(
        "handler_name",
        choices=handler_ids,
        help=f"Run the handler for the specified handler name. Valid options are: \n{'\n'.join(handler_ids)}",
    )
    parser.add_argument(
        "--start-date",
        dest="start_date",
        help="Specify the start date for the handler in YYYY-MM-DD format.",
    )
    parser.add_argument(
        "--end-date",
        dest="end_date",
        help="Specify the end date for the handler in YYYY-MM-DD format.",
    )

    args = parser.parse_args()
    if args.handler_name == "listings_by_market":
        handle_listings_by_market()
    elif args.handler_name == "markets_peak_months":
        handle_markets_peak_months()
    elif args.handler_name == "markets_summaries":
        handle_markets_summaries()
    elif args.handler_name == "exchange_rate":
        handle_exchange_rate(start_date=args.start_date, end_date=args.end_date)
    else:
        logger.error(
            f"Invalid handler name: '{args.handler_name}'. Valid options are: {handler_ids}"
        )
