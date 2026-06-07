#!/usr/bin/env python3

from __future__ import annotations

from api.crons.handlers import handle_markets_summaries
from utils.logging.init import init_logging

logger = init_logging(__name__)

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
