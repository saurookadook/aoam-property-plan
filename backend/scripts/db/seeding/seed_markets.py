#!/usr/bin/env python3
from __future__ import annotations

import json
import traceback
from datetime import datetime, timezone
from sqlalchemy import select, and_
from rich import inspect as ri

from db.db_session_manager import DBSessionManager
from models.market.db import MarketDB
from models.market.facade import MarketFacade
from models.market_financial_report.facade import MarketFinancialReportFacade
from utils.filesystem import get_module_root
from utils.logging.init import init_logging

root_logger = init_logging(__file__)

REQUIRED_FIGURES = (
    "average_daily_rate",
    "occupancy",
    "revenue",
    "active_listings_count",
)
"""
What a capture has to carry before it is worth a row.

``adr_cop``, ``occupancy_rate``, ``annual_revenue_cop`` and ``listing_count`` are
all ``NOT NULL`` on ``market_financial_reports``, so a capture missing any of
them cannot produce a report - and a market with no report is invisible to every
read path Phase 4 adds. Checked up front so the failure names the file and the
missing field, rather than surfacing as an ``IntegrityError`` further down.

See ``seed_data/pending/`` for the placeholder captures this exists to catch.
"""


def seed_db_with_markets():
    local_db_session = DBSessionManager().scoped_session()

    seed_data_dir = (
        get_module_root(__file__) / "scripts" / "db" / "seeding" / "seed_data"
    )

    failed_exceptions = []
    market_facade = MarketFacade(db_session=local_db_session)
    market_financial_report_facade = MarketFinancialReportFacade(
        db_session=local_db_session
    )

    for json_summary in seed_data_dir.glob("*.json"):
        with open(json_summary, "r") as f:
            try:
                market_data = json.load(f)
                ri(market_data, sort=True, title="'market_data' from JSON file")
                market_details = market_data.get("market")

                missing_figures = [
                    figure
                    for figure in REQUIRED_FIGURES
                    if market_data.get(figure) is None
                ]
                if missing_figures:
                    raise ValueError(
                        f"'{json_summary.name}' is missing "
                        f"[{', '.join(missing_figures)}] - capture the summary "
                        f"before seeding it (see 'seed_data/pending/README.md')"
                    )

                market_dict = dict(
                    country=market_details.get("country"),
                    district=market_details.get("district", None),
                    locality=market_details.get("locality"),
                    region=market_details.get("region"),
                )

                maybe_one = local_db_session.execute(
                    select(MarketDB).where(
                        and_(
                            MarketDB.locality == market_dict.get("locality"),
                            MarketDB.country == market_dict.get("country"),
                            MarketDB.region == market_dict.get("region"),
                        )
                    )
                ).scalar_one_or_none()

                ri(maybe_one, sort=True, title="'maybe_one' from 'market_data'")

                if maybe_one is not None:
                    market_dict["id"] = maybe_one.id

                market_record = market_facade.create_or_update(payload=market_dict)
                local_db_session.commit()

                ri(market_record, sort=True, title="'market_record' from 'market_data'")

                # Refreshes the market's latest report rather than skipping the
                # market, which is what this did. A seed script that only works
                # once on a clean database is not a seed script: re-running it
                # after re-capturing ``seed_data/`` has to move the figures, or
                # the only way to update a market is to delete its rows by hand.
                latest_report = market_financial_report_facade.get_latest_by_market_id(
                    market_record.id
                )

                market_financial_report_dict = dict(
                    market_id=market_record.id,
                    adr_cop=market_data.get("average_daily_rate", 0),
                    annual_revenue_cop=market_data.get("revenue", 0),
                    listing_count=market_data.get("active_listings_count"),
                    last_updated=market_data.get(
                        "last_updated", datetime.now(timezone.utc)
                    ),
                    occupancy_rate=market_data.get("occupancy"),
                )

                # ``peak_months`` and ``monthly_revenue_distribution`` are set
                # only when the capture actually carries them, which
                # ``/markets/summary`` never has - both come from the centroid
                # estimate ``handle_markets_peak_months`` makes. Sending them
                # unconditionally would have refreshing the headline figures
                # blank the seasonality of every market on the way past.
                for seasonality_field in (
                    "monthly_revenue_distribution",
                    "peak_months",
                ):
                    if market_data.get(seasonality_field) is not None:
                        market_financial_report_dict[seasonality_field] = market_data[
                            seasonality_field
                        ]

                if latest_report is not None:
                    market_financial_report_dict["id"] = latest_report.id
                    root_logger.info(
                        f"Refreshing market financial report with ``id``: "
                        f"'{latest_report.id}' for market with ``id``: "
                        f"'{market_record.id}'"
                    )

                market_financial_report_facade.create_or_update(
                    payload=market_financial_report_dict
                )
                local_db_session.commit()
            except Exception as e:
                local_db_session.rollback()
                e.add_note(f"Failed to seed market from '{f.name}'")
                root_logger.exception(e)
                failed_exceptions.append(
                    "\n".join(traceback.format_tb(e.__traceback__))
                )

    if failed_exceptions:
        root_logger.error(f"Failed to seed {len(failed_exceptions)} markets.")
        for e in failed_exceptions:
            root_logger.error(e)


if __name__ == "__main__":
    seed_db_with_markets()
