#!/usr/bin/env python3
from __future__ import annotations

import json
import traceback
import sys
from datetime import datetime, timezone
from sqlalchemy import select, and_
from rich import inspect as ri

from db.db_session_manager import DBSessionManager
from models.listing.facade import ListingFacade
from models.listing_financial_report.facade import ListingFinancialReportFacade
from models.market.db import MarketDB
from utils.filesystem import get_project_root
from utils.logging.init import init_logging

logger = init_logging(__file__)


def seed_db_with_listings():
    local_db_session = DBSessionManager().scoped_session()

    current_date = datetime.now(timezone.utc).date()
    seed_data_dir = (
        get_project_root(__file__) / "_research" / "listings" / "search-by-market"
    )

    failed_exceptions = []
    listing_facade = ListingFacade(db_session=local_db_session)
    listing_financial_report_facade = ListingFinancialReportFacade(
        db_session=local_db_session
    )

    for response_file in seed_data_dir.glob("*.json"):
        with open(response_file, "r") as f:
            data = json.load(f)
            ri(data, sort=True)

            for listing_result in data["results"]:
                location_info = listing_result["location_info"]
                listing_info = listing_result["listing_info"]
                property_details = listing_result["property_details"]

                try:
                    maybe_market = local_db_session.execute(
                        select(MarketDB).where(
                            and_(
                                MarketDB.locality == location_info.get("locality"),
                                MarketDB.country == location_info.get("country"),
                                MarketDB.region == location_info.get("region"),
                            )
                        )
                    ).scalar_one_or_none()

                    if maybe_market is None:
                        raise ValueError(
                            f"Market not found for listing {listing_info['listing_id']}"
                        )

                    market = maybe_market

                    listing_record = listing_facade.create_or_update(
                        payload={
                            "airroi_id": listing_info["listing_id"],
                            "amenities": property_details.get("amenities", []),
                            "baths": property_details.get("baths", None),
                            "beds": property_details.get("beds", None),
                            "bedrooms": property_details["bedrooms"],
                            "cover_photo_url": listing_info["cover_photo_url"],
                            "description": listing_info.get("description", None),
                            "latitude": location_info.get("latitude", None),
                            "location": f"POINT({location_info['longitude']} {location_info['latitude']})",
                            "longitude": location_info.get("longitude", None),
                            "market_id": market.id,
                            "name": listing_info.get("listing_name", None),
                            "photo_urls": listing_info.get("photo_urls", []),
                            "property_type": listing_info["listing_type"],
                            "source_url": listing_info.get("source_url", None),
                        }
                    )
                except Exception as e:
                    error_message = (
                        f"Error processing listing {listing_info['listing_id']}: {e}"
                    )
                    logger.error(error_message)
                    logger.error(traceback.format_exc())
                    failed_exceptions.append((error_message, traceback.format_exc()))
                    continue

                if listing_financial_report_facade.has_one_by_listing_id_for_date(
                    listing_id=listing_record.id, target_date_str=str(current_date)
                ):
                    continue

                try:
                    ratings = dict(listing_result.get("ratings", {}) or {})
                    ratings["number_of_reviews"] = ratings.pop("num_reviews", None)

                    metrics = dict(listing_result.get("performance_metrics", {}) or {})
                    metrics["ttm_occupancy_rate"] = metrics.pop("ttm_occupancy", None)
                    metrics["ttm_adjusted_occupancy_rate"] = metrics.pop(
                        "ttm_adjusted_occupancy", None
                    )
                    metrics["l90d_occupancy_rate"] = metrics.pop("l90d_occupancy", None)
                    metrics["l90d_adjusted_occupancy_rate"] = metrics.pop(
                        "l90d_adjusted_occupancy", None
                    )

                    listing_financial_report_facade.create_or_update(
                        payload={
                            "listing_id": listing_record.id,
                            **ratings,
                            **metrics,
                        }
                    )
                    local_db_session.commit()
                    logger.info(
                        f"Finished creating/updating listing financial report for market with id='{market.id}' "
                        f"(locality='{market.locality}'  |  airroi_id='{listing_info['listing_id']}')"
                    )
                except Exception as e:
                    logger.error(
                        f"Error creating/updating listing financial report for market with id='{market.id}' "
                        f"(locality='{market.locality}'  |  airroi_id='{listing_info['listing_id']}'): {e}",
                        exc_info=sys.exc_info(),
                    )
                    local_db_session.rollback()
                    local_db_session.commit()
                    continue
                local_db_session.commit()
            local_db_session.commit()

    local_db_session.close()
    DBSessionManager().scoped_session.remove()


if __name__ == "__main__":
    seed_db_with_listings()
