from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import cast

import requests

from config.env_var_manager import EnvVarManager
from constants import AIRROI_BASE_URL
from db.db_session_manager import DBSessionManager
from models.listing.facade import ListingFacade
from models.listing_financial_report.facade import ListingFinancialReportFacade
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


def handle_listings_by_market():
    local_db_session = DBSessionManager().scoped_session()
    market_facade = MarketFacade(db_session=local_db_session)
    listing_facade = ListingFacade(db_session=local_db_session)
    listing_financial_report_facade = ListingFinancialReportFacade(
        db_session=local_db_session
    )

    all_markets = market_facade.get_all()
    env_vars = EnvVarManager().env_vars
    request_headers = {
        "Content-Type": "application/json",
        "x-api-key": env_vars.airroi_api_key,
    }

    should_continue_for_locality = {market.locality: True for market in all_markets}

    for i in range(5):
        logger.info(f"Handling page {i} for all markets")

        for market in all_markets:
            if not should_continue_for_locality.get(market.locality, True):
                continue

            logger.info(
                f"Handling listings for market with id='{market.id}' "
                f"and locality='{market.locality}'"
            )
            try:
                response = requests.post(
                    f"{AIRROI_BASE_URL}/listings/search/market",
                    headers=request_headers,
                    json={
                        "market": {
                            "country": market.country,
                            "region": market.region,
                            "locality": market.locality,
                        },
                        "filter": {
                            "room_type": {
                                "eq": "entire_home",
                            },
                            "bedrooms": {
                                "range": [1, 3],
                            },
                        },
                        "sort": {
                            "ttm_revenue": "desc",
                        },
                        "pagination": {
                            "offset": i,
                            "page_size": 10,
                        },
                        "currency": "native",
                    },
                    timeout=30,
                )
                response.raise_for_status()
                result = response.json()
            except (ValueError, requests.RequestException) as e:
                logger.error(
                    f"Error fetching listings for market with id='{market.id}' "
                    f"and locality='{market.locality}': {e}"
                )
                should_continue_for_locality[market.locality] = False
                continue

            for listing_result in result.get("results", []):
                listing_info = listing_result["listing_info"]

                try:
                    location_info = listing_result["location_info"]
                    property_details = listing_result["property_details"]

                    listing_lat = location_info["latitude"]
                    listing_lng = location_info["longitude"]

                    listing_record = listing_facade.create_or_update(
                        payload={
                            "airroi_id": listing_info["listing_id"],
                            "bedrooms": property_details["bedrooms"],
                            "cover_photo_url": listing_info["cover_photo_url"],
                            "latitude": listing_lat,
                            "location": f"POINT({listing_lng} {listing_lat})",
                            "longitude": listing_lng,
                            "market_id": market.id,
                            "property_type": listing_info["listing_type"],
                        }
                    )
                    local_db_session.commit()
                    logger.info(
                        f"Finished creating/updating listing for market with id='{market.id}' "
                        f"(locality='{market.locality}'  |  airroi_id='{listing_info['listing_id']}')"
                    )
                except Exception as e:
                    logger.error(
                        f"Error creating/updating listing for market with id='{market.id}' "
                        f"(locality='{market.locality}'  |  airroi_id='{listing_info['listing_id']}'): {e}"
                    )
                    local_db_session.rollback()
                    local_db_session.commit()
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
                        f"(locality='{market.locality}'  |  airroi_id='{listing_info['listing_id']}'): {e}"
                    )
                    local_db_session.rollback()
                    local_db_session.commit()
                    continue
            local_db_session.commit()
        local_db_session.commit()
    local_db_session.commit()
    local_db_session.close()
    DBSessionManager().scoped_session.remove()
