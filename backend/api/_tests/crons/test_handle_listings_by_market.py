from __future__ import annotations

import json
from collections import defaultdict
from typing import Any, Callable, Generator

import pytest
from sqlalchemy import select

from _factories.market.db import MarketDBFactory
from api.crons.handlers import handle_listings_by_market
from models.listing.db import ListingDB
from models.listing.facade import ListingFacade
from models.listing_financial_report.db import ListingFinancialReportDB
from models.listing_financial_report.facade import ListingFinancialReportFacade
from models.market.db import MarketDB
from models.market.facade import MarketFacade
from utils.filesystem import get_project_root


@pytest.fixture
def listings_by_market_response_dicts_by_locality() -> dict[str, list[dict]]:
    responses_path = (
        get_project_root(__file__) / "_research" / "listings" / "search-by-market"
    )
    response_files_by_locality = defaultdict(list)
    for response_file in responses_path.glob("*.json"):
        with open(response_file, "r") as f:
            data = json.load(f)
            locality = data["results"][0]["location_info"]["locality"]
            response_files_by_locality[locality].append(data)
            response_files_by_locality[locality].sort(
                key=lambda x: x["pagination"]["offset"]
            )
    return response_files_by_locality


@pytest.fixture
def listings_by_market_dynamic_resp_callback(
    listings_by_market_response_dicts_by_locality,
) -> Callable[..., dict]:
    def _matcher(request, context):
        request_body = json.loads(request.body)
        req_locality = request_body["market"]["locality"]
        req_offset = request_body["pagination"]["offset"]
        req_page_size = request_body["pagination"]["page_size"]

        paged_responses = listings_by_market_response_dicts_by_locality.get(
            req_locality, None
        )

        # AirROI's ``offset`` counts records rather than pages, so the page index
        # has to be recovered from it. A remainder means the caller is stepping by
        # something other than a page - the bug this fixture used to enshrine, by
        # indexing pages with the raw offset.
        page_index, remainder = divmod(req_offset, req_page_size)

        if (
            paged_responses is None
            or remainder
            or page_index > len(paged_responses) - 1
        ):
            context.status_code = 404
            return {}

        response_page = paged_responses[page_index]
        context.status_code = 200
        return response_page

    return _matcher


@pytest.fixture
def airroi_request_mocks(
    listings_by_market_dynamic_resp_callback, http_requests_mock
) -> Generator[Any, Any, None]:
    http_requests_mock.post(
        "https://api.airroi.com/listings/search/market",
        json=listings_by_market_dynamic_resp_callback,
    )
    yield http_requests_mock


class TestHandleListingsByMarket:
    @pytest.fixture
    def listing_facade(self, test_db_session):
        return ListingFacade(db_session=test_db_session)

    @pytest.fixture
    def listing_financial_report_facade(self, test_db_session):
        return ListingFinancialReportFacade(db_session=test_db_session)

    @pytest.fixture
    def market_facade(self, test_db_session):
        return MarketFacade(db_session=test_db_session)

    @pytest.fixture
    def market_records(self, markets_data, test_db_session):
        markets = [MarketDBFactory(**market_dict) for market_dict in markets_data]
        test_db_session.commit()
        return markets

    def test_handle_listings_by_market(
        self,
        airroi_request_mocks,
        listing_facade: ListingFacade,
        listing_financial_report_facade: ListingFinancialReportFacade,
        listings_by_market_response_dicts_by_locality: dict[str, list[dict]],
        market_facade: MarketFacade,
        market_records: list[MarketDB],
        # markets_data_from_responses,
        test_db_session,
    ):
        listings_before = test_db_session.execute(select(ListingDB)).scalars().all()
        assert len(listings_before) == 0
        listing_financial_reports_before = (
            test_db_session.execute(select(ListingFinancialReportDB)).scalars().all()
        )
        assert len(listing_financial_reports_before) == 0

        handle_listings_by_market()

        listings_after = test_db_session.execute(select(ListingDB)).scalars().all()
        assert len(listings_after) >= 30
        listing_financial_reports_after = (
            test_db_session.execute(select(ListingFinancialReportDB)).scalars().all()
        )
        assert len(listing_financial_reports_after) >= 30

        lfr_listing_id_set = {lfr.listing_id for lfr in listing_financial_reports_after}
        assert len(lfr_listing_id_set) == len(listing_financial_reports_after)

        # ``offset`` counts records, not pages. Paging stops at the first 404, and
        # only two pages per locality are captured, so the third request is the
        # last one - but it is the step from 0 to 10 to 20 that matters here.
        offsets_by_locality = defaultdict(list)
        for sent_request in airroi_request_mocks.request_history:
            sent_body = sent_request.json()
            offsets_by_locality[sent_body["market"]["locality"]].append(
                sent_body["pagination"]["offset"]
            )

        assert offsets_by_locality["Salento"] == [0, 10, 20]

        all_markets = market_facade.get_all()

        for (
            locality,
            response_files,
        ) in listings_by_market_response_dicts_by_locality.items():
            market = next((m for m in all_markets if m.locality == locality), None)
            assert market is not None, f"Market not found for locality='{locality}'"

            for response_file in response_files:
                results = response_file["results"]

                for listing_result in results:
                    listing_info = listing_result["listing_info"]
                    location_info = listing_result["location_info"]
                    property_details = listing_result["property_details"]
                    ratings = listing_result["ratings"]
                    performance_metrics = listing_result["performance_metrics"]

                    listing_record = listing_facade.get_one_by_airroi_id(
                        int(listing_info["listing_id"])
                    )

                    assert listing_record.airroi_id == int(listing_info["listing_id"])
                    assert listing_record.amenities == property_details.get(
                        "amenities", []
                    )
                    assert listing_record.baths == property_details.get("baths", None)
                    assert listing_record.beds == property_details.get("beds", None)
                    assert listing_record.bedrooms == property_details["bedrooms"]
                    assert (
                        listing_record.cover_photo_url
                        == listing_info["cover_photo_url"]
                    )
                    assert listing_record.description == listing_info.get(
                        "description", None
                    )
                    assert listing_record.latitude == location_info["latitude"]
                    assert listing_record.longitude == location_info["longitude"]
                    assert listing_record.market_id == market.id
                    assert listing_record.name == listing_info.get("listing_name", None)
                    assert listing_record.photo_urls == listing_info.get(
                        "photo_urls", []
                    )
                    assert listing_record.property_type == listing_info["listing_type"]

                    listing_financial_report_record_by_list = (
                        listing_financial_report_facade.get_all_by_listing_id(
                            listing_record.id
                        )
                    )

                    listing_financial_report_record = next(
                        (
                            listing
                            for listing in listing_financial_report_record_by_list
                            if listing.listing_id == listing_record.id
                        ),
                        None,
                    )

                    assert listing_financial_report_record is not None
                    assert (
                        listing_financial_report_record.listing_id == listing_record.id
                    )
                    assert (
                        listing_financial_report_record.number_of_reviews
                        == ratings.get("num_reviews", None)
                    )
                    assert (
                        listing_financial_report_record.rating_overall
                        == ratings.get("rating_overall", None)
                    )
                    assert (
                        listing_financial_report_record.rating_accuracy
                        == ratings.get("rating_accuracy", None)
                    )
                    assert (
                        listing_financial_report_record.rating_checkin
                        == ratings.get("rating_checkin", None)
                    )
                    assert (
                        listing_financial_report_record.rating_cleanliness
                        == ratings.get("rating_cleanliness", None)
                    )
                    assert (
                        listing_financial_report_record.rating_communication
                        == ratings.get("rating_communication", None)
                    )
                    assert (
                        listing_financial_report_record.rating_location
                        == ratings.get("rating_location", None)
                    )
                    assert listing_financial_report_record.rating_value == ratings.get(
                        "rating_value", None
                    )

                    assert (
                        listing_financial_report_record.ttm_revenue
                        == performance_metrics.get("ttm_revenue", None)
                    )
                    assert (
                        listing_financial_report_record.ttm_avg_rate
                        == performance_metrics.get("ttm_avg_rate", None)
                    )
                    assert (
                        listing_financial_report_record.ttm_occupancy_rate
                        == performance_metrics.get("ttm_occupancy", None)
                    )
                    assert (
                        listing_financial_report_record.ttm_adjusted_occupancy_rate
                        == performance_metrics.get("ttm_adjusted_occupancy", None)
                    )
                    assert (
                        listing_financial_report_record.ttm_revpar
                        == performance_metrics.get("ttm_revpar", None)
                    )
                    assert (
                        listing_financial_report_record.ttm_adjusted_revpar
                        == performance_metrics.get("ttm_adjusted_revpar", None)
                    )
                    assert (
                        listing_financial_report_record.ttm_total_days
                        == performance_metrics.get("ttm_total_days", None)
                    )
                    assert (
                        listing_financial_report_record.ttm_available_days
                        == performance_metrics.get("ttm_available_days", None)
                    )
                    assert (
                        listing_financial_report_record.ttm_blocked_days
                        == performance_metrics.get("ttm_blocked_days", None)
                    )
                    assert (
                        listing_financial_report_record.ttm_days_reserved
                        == performance_metrics.get("ttm_days_reserved", None)
                    )
                    assert (
                        listing_financial_report_record.ttm_avg_min_nights
                        == performance_metrics.get("ttm_avg_min_nights", None)
                    )
                    assert (
                        listing_financial_report_record.ttm_avg_length_of_stay
                        == performance_metrics.get("ttm_avg_length_of_stay", None)
                    )
                    assert (
                        listing_financial_report_record.l90d_revenue
                        == performance_metrics.get("l90d_revenue", None)
                    )
                    assert (
                        listing_financial_report_record.l90d_avg_rate
                        == performance_metrics.get("l90d_avg_rate", None)
                    )
                    assert (
                        listing_financial_report_record.l90d_occupancy_rate
                        == performance_metrics.get("l90d_occupancy", None)
                    )
                    assert (
                        listing_financial_report_record.l90d_adjusted_occupancy_rate
                        == performance_metrics.get("l90d_adjusted_occupancy", None)
                    )
                    assert (
                        listing_financial_report_record.l90d_revpar
                        == performance_metrics.get("l90d_revpar", None)
                    )
                    assert (
                        listing_financial_report_record.l90d_adjusted_revpar
                        == performance_metrics.get("l90d_adjusted_revpar", None)
                    )
                    assert (
                        listing_financial_report_record.l90d_total_days
                        == performance_metrics.get("l90d_total_days", None)
                    )
                    assert (
                        listing_financial_report_record.l90d_available_days
                        == performance_metrics.get("l90d_available_days", None)
                    )
                    assert (
                        listing_financial_report_record.l90d_blocked_days
                        == performance_metrics.get("l90d_blocked_days", None)
                    )
                    assert (
                        listing_financial_report_record.l90d_days_reserved
                        == performance_metrics.get("l90d_days_reserved", None)
                    )
                    assert (
                        listing_financial_report_record.l90d_avg_min_nights
                        == performance_metrics.get("l90d_avg_min_nights", None)
                    )
                    assert (
                        listing_financial_report_record.l90d_avg_length_of_stay
                        == performance_metrics.get("l90d_avg_length_of_stay", None)
                    )
