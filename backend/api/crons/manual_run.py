#!/usr/bin/env python3

from __future__ import annotations

from api.crons.handlers import handle_listings_by_market, handle_markets_summaries
from utils.logging.init import init_logging

logger = init_logging(__name__)

if __name__ == "__main__":
    import argparse

    handler_ids = [
        "listings_by_market",
        "markets_summaries",
    ]

    parser = argparse.ArgumentParser(description="Manually run cron handlers")
    parser.add_argument(
        "handler_name",
        choices=handler_ids,
        help=f"Run the handler for the specified handler name. Valid options are: \n{'\n'.join(handler_ids)}",
    )

    args = parser.parse_args()
    if args.handler_name == "listings_by_market":
        handle_listings_by_market()
    elif args.handler_name == "markets_summaries":
        handle_markets_summaries()
    else:
        logger.error(
            f"Invalid handler name: '{args.handler_name}'. Valid options are: {handler_ids}"
        )
