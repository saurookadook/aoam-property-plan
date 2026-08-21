from __future__ import annotations

import logging
import statistics
import sys
from datetime import datetime, timezone
from typing import Optional, cast

import requests
from sqlalchemy import Date, exists, func, select

from db.db_session_manager import DBSessionManager
from models.exchange_rate.facade import ExchangeRateFacade
from models.listing.facade import ListingFacade
from models.listing_financial_report.db import ListingFinancialReportDB
from models.listing_financial_report.facade import ListingFinancialReportFacade
from models.market.entity import MarketEntity
from models.market.facade import MarketFacade
from models.market_financial_report.facade import MarketFinancialReportFacade
from services import airroi
from services.exceptions import AirROIError
from services.property_analysis import GUESTS_PER_BEDROOM, peak_months
from utils.logging.extended_logger import ExtendedLogger

logger = cast(ExtendedLogger, logging.getLogger(__name__))

PAGE_COUNT = 5
"""
Pages of listings to pull per market per run - 50 listings at the default page
size.
"""


def handle_markets_summaries():
    local_db_session = DBSessionManager().scoped_session()
    market_facade = MarketFacade(db_session=local_db_session)
    market_financial_report_facade = MarketFinancialReportFacade(
        db_session=local_db_session
    )

    all_markets = market_facade.get_all()

    for market in all_markets:
        logger.info(
            f"Handling market summary for market with id='{market.id}' "
            f"and locality='{market.locality}'"
        )
        try:
            result = airroi.get_market_summary(market)
        except AirROIError as e:
            logger.error(
                f"Error fetching market summary for market with id='{market.id}' "
                f"and locality='{market.locality}': {e}",
                exc_info=sys.exc_info(),
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
                    # NOTE: this endpoint has never returned ``peak_months``, so
                    # this has always resolved to ``None``.
                    # ``handle_markets_peak_months`` is what actually fills the
                    # column, from ``/calculator/estimate``.
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
                f"and locality='{market.locality}': {e}",
                exc_info=sys.exc_info(),
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

    current_date = datetime.now(timezone.utc).date()

    all_markets = market_facade.get_all()

    should_continue_for_locality = {market.locality: True for market in all_markets}

    for page_index in range(PAGE_COUNT):
        logger.info(f"Handling page {page_index} for all markets")

        for market in all_markets:
            if not should_continue_for_locality.get(market.locality, True):
                continue

            logger.info(
                f"Handling listings for market with id='{market.id}' "
                f"and locality='{market.locality}'"
            )
            try:
                # AirROI's ``offset`` counts records, not pages. Sending the page
                # index straight through - as this did - re-requested the same
                # listings shifted by one, so a market yielded ~14 distinct
                # listings per run instead of 50.
                result = airroi.search_listings_by_market(
                    market, offset=page_index * airroi.DEFAULT_PAGE_SIZE
                )
            except AirROIError as e:
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
                            "amenities": property_details.get("amenities", []),
                            "baths": property_details.get("baths", None),
                            "beds": property_details.get("beds", None),
                            "bedrooms": property_details["bedrooms"],
                            "cover_photo_url": listing_info["cover_photo_url"],
                            "description": listing_info.get("description", None),
                            "latitude": listing_lat,
                            "location": f"POINT({listing_lng} {listing_lat})",
                            "longitude": listing_lng,
                            "market_id": market.id,
                            "name": listing_info.get("listing_name", None),
                            "photo_urls": listing_info.get("photo_urls", []),
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
                        f"(locality='{market.locality}'  |  airroi_id='{listing_info['listing_id']}'): {e}",
                        exc_info=sys.exc_info(),
                    )
                    local_db_session.rollback()
                    local_db_session.commit()
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
    local_db_session.commit()
    local_db_session.close()
    DBSessionManager().scoped_session.remove()


def handle_markets_peak_months():
    """
    Fills ``market_financial_reports.peak_months`` from a centroid estimate.

    The only route to that column. ``/markets/summary`` has never returned
    ``peak_months`` and AirROI publishes no ``/markets/seasonality`` endpoint
    despite the execution plan citing one; ``monthly_revenue_distributions`` on
    ``/calculator/estimate`` is the only seasonality it exposes, and that endpoint
    takes a point rather than a market. So a market is reduced to the average
    position of the listings already ingested for it, described by their median
    size, and asked about as though it were one property.

    Runs after ``handle_markets_summaries``: it updates the latest report rather
    than creating one, because seasonality is an attribute of the figures in that
    report, not a report of its own.
    """
    local_db_session = DBSessionManager().scoped_session()
    market_facade = MarketFacade(db_session=local_db_session)
    listing_facade = ListingFacade(db_session=local_db_session)
    market_financial_report_facade = MarketFinancialReportFacade(
        db_session=local_db_session
    )

    for market in market_facade.get_all():
        logger.info(
            f"Handling peak months for market with id='{market.id}' "
            f"and locality='{market.locality}'"
        )

        latest_report = market_financial_report_facade.get_latest_by_market_id(
            market.id
        )
        if latest_report is None:
            logger.warning(
                f"No market financial report for market with id='{market.id}' "
                f"and locality='{market.locality}' - run 'markets_summaries' first"
            )
            continue

        centroid = _market_centroid(listing_facade, market_facade, market)
        if centroid is None:
            continue

        latitude, longitude, bedrooms, baths = centroid

        try:
            estimate = airroi.get_revenue_estimate(
                latitude=latitude,
                longitude=longitude,
                bedrooms=bedrooms,
                baths=baths,
                guests=bedrooms * GUESTS_PER_BEDROOM,
            )
        except AirROIError as e:
            logger.error(
                f"Error fetching a centroid estimate for market with "
                f"id='{market.id}' and locality='{market.locality}': {e}",
                exc_info=sys.exc_info(),
            )
            continue

        distribution = estimate.get("monthly_revenue_distributions") or []
        months = peak_months(distribution)
        if not months:
            logger.warning(
                f"Centroid estimate for market with id='{market.id}' and "
                f"locality='{market.locality}' carried no monthly distribution"
            )
            continue

        try:
            # The distribution is stored as well as the three names derived from
            # it. It was already being fetched and thrown away, and a market-level
            # seasonality chart cannot be drawn from three strings.
            market_financial_report_facade.update(
                payload={
                    "id": latest_report.id,
                    "monthly_revenue_distribution": distribution,
                    "peak_months": months,
                }
            )
            local_db_session.commit()
            logger.info(
                f"Finished handling peak months for market with id='{market.id}' "
                f"and locality='{market.locality}' - {months}"
            )
        except Exception as e:
            logger.error(
                f"Error writing peak months for market with id='{market.id}' "
                f"and locality='{market.locality}': {e}",
                exc_info=sys.exc_info(),
            )
            local_db_session.rollback()
            continue

    local_db_session.commit()
    local_db_session.close()
    DBSessionManager().scoped_session.remove()


def _market_centroid(
    listing_facade: ListingFacade,
    market_facade: MarketFacade,
    market: MarketEntity,
) -> Optional[tuple[float, float, int, float]]:
    """
    Reduces a market's ingested listings to one point and one typical property.

    ``markets`` holds no coordinates - only country/region/locality/district - so
    the listings are the only thing that can say where a market is.

    The point comes from ``MarketFacade.get_centroid_by_id`` rather than being
    averaged here, so the marker ``/markets`` plots and the estimate this feeds to
    AirROI cannot drift apart: a market's seasonality has to be reported for the
    place the map says it is. The typical size stays local because it is a median
    over the ingested rows, which the read path has no use for.

    Returns ``None`` when the market cannot describe itself. Bath count is
    required by AirROI and a fabricated one silently changes which comps come
    back, so a market whose listings all lack ``baths`` is skipped rather than
    guessed at - the same rule ``services.property_analysis`` applies to a
    property.
    """
    centroid = market_facade.get_centroid_by_id(market.id)

    if centroid is None:
        logger.warning(
            f"No ingested listings for market with id='{market.id}' and "
            f"locality='{market.locality}' - run 'listings_by_market' first"
        )
        return None

    listings = listing_facade.get_all_by_market_id(market.id)

    baths_values = [listing.baths for listing in listings if listing.baths is not None]
    if not baths_values:
        logger.warning(
            f"No ingested listing for market with id='{market.id}' and "
            f"locality='{market.locality}' reports a bath count - skipping"
        )
        return None

    # ``median`` of an even-length run of integers can land on a half, and
    # bedrooms is an integer input; at least one bedroom, whatever the rounding.
    bedrooms = max(
        1, round(statistics.median(listing.bedrooms for listing in listings))
    )

    return (
        centroid.latitude,
        centroid.longitude,
        bedrooms,
        float(statistics.median(baths_values)),
    )


def handle_exchange_rate(
    *, start_date: Optional[str] = None, end_date: Optional[str] = None
):
    local_db_session = DBSessionManager().scoped_session()
    exchange_rate_facade = ExchangeRateFacade(db_session=local_db_session)

    current_date = datetime.now(timezone.utc).date()

    date_params: list[str] = []

    if start_date:
        try:
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
            date_params.append(f"from={start_date_obj}")
        except ValueError as e:
            logger.error(
                f"Invalid start date format: {start_date}. Expected YYYY-MM-DD.",
                exc_info=sys.exc_info(),
            )
            pass
    if end_date:
        try:
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
            date_params.append(f"to={end_date_obj}")
        except ValueError as e:
            logger.error(
                f"Invalid end date format: {end_date}. Expected YYYY-MM-DD.",
                exc_info=sys.exc_info(),
            )
            pass

    if not date_params:
        date_params.append(f"date={current_date}")

    try:
        response = requests.get(
            f"https://api.frankfurter.dev/v2/rates?base=USD&quotes=COP&{'&'.join(date_params)}",
            headers={
                "Content-Type": "application/json",
            },
            timeout=30,
        )
        response.raise_for_status()
        result = response.json()
    except Exception as e:
        logger.error(
            f"Error fetching exchange rate for date='{current_date}' with params='{date_params}': {e}",
            exc_info=sys.exc_info(),
        )
        local_db_session.close()
        DBSessionManager().scoped_session.remove()
        return

    for rate_record in result:
        try:
            stmt = select(
                exists().where(
                    func.cast(ListingFinancialReportDB.created_at, Date)
                    == datetime.strptime(rate_record["date"], "%Y-%m-%d").date()
                )
            )

            has_listing_financial_report_for_date = local_db_session.execute(
                stmt
            ).scalar()

            if not has_listing_financial_report_for_date:
                logger.warning(
                    f"No listing financial report found for date='{rate_record['date']}'. Skipping exchange rate update."
                )
                continue

            exchange_rate_facade.create_or_update(
                payload={
                    "record_date": rate_record["date"],
                    "cop_per_usd": rate_record["rate"],
                }
            )
        except Exception as e:
            logger.error(
                f"Error creating/updating exchange rate record for date='{rate_record['date']}': {e}",
                exc_info=sys.exc_info(),
            )
            local_db_session.rollback()
            continue

    local_db_session.commit()
    local_db_session.close()
    DBSessionManager().scoped_session.remove()
