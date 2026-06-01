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
                ri(market_data, sort=True)
                market_details = market_data.get("market")

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

                if maybe_one is not None:
                    market_dict["id"] = maybe_one.id

                market_record = market_facade.create_or_update(payload=market_dict)
                local_db_session.commit()

                market_financial_report_dict = dict(
                    market_id=market_record.id,
                    adr_usd=market_data.get("average_daily_rate", 0),
                    annual_revenue_usd=market_data.get("revenue", 0),
                    listing_count=market_data.get("active_listings_count"),
                    last_updated=market_data.get(
                        "last_updated", datetime.now(timezone.utc)
                    ),
                    occupancy_rate=market_data.get("occupancy"),
                    peak_months=market_data.get("peak_months", None),
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
