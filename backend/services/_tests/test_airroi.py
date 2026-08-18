from __future__ import annotations

import json
from urllib.parse import parse_qs

import pytest
import requests

from _factories.market.entity import MarketEntityFactory
from constants import AIRROI_BASE_URL
from services import airroi
from services.exceptions import AirROIError
from utils.filesystem import get_project_root

ESTIMATE_URL = f"{AIRROI_BASE_URL}/calculator/estimate"
COMPARABLES_URL = f"{AIRROI_BASE_URL}/listings/comparables"
MARKET_SUMMARY_URL = f"{AIRROI_BASE_URL}/markets/summary"
SEARCH_MARKET_URL = f"{AIRROI_BASE_URL}/listings/search/market"


@pytest.fixture
def salento_market():
    return MarketEntityFactory(
        country="Colombia", region="Quindío", locality="Salento", district=None
    )


@pytest.fixture
def salento_3br_estimate() -> dict:
    capture = (
        get_project_root(__file__)
        / "_research"
        / "calculator"
        / "estimate"
        / "salento_quindio_colombia__2-baths_3-bedrooms_8-guests.json"
    )
    with open(capture, "r") as capture_json:
        return json.load(capture_json)


class TestGetRevenueEstimate:
    def test_returns_the_decoded_body(self, http_requests_mock, salento_3br_estimate):
        http_requests_mock.get(ESTIMATE_URL, json=salento_3br_estimate)

        result = airroi.get_revenue_estimate(
            latitude=4.6375, longitude=-75.5703, bedrooms=3, baths=2, guests=8
        )

        assert result["percentiles"]["revenue"]["p25"] == pytest.approx(36074113.0)
        assert result["currency"] == "COP"
        assert len(result["comparable_listings"]) == 25

    def test_sends_the_documented_query_and_nothing_else(
        self, http_requests_mock, salento_3br_estimate
    ):
        mocked = http_requests_mock.get(ESTIMATE_URL, json=salento_3br_estimate)

        airroi.get_revenue_estimate(
            latitude=4.6375, longitude=-75.5703, bedrooms=3, baths=2, guests=8
        )

        # No ``currency``: the captures come back "COP" without one, and guessing
        # at an undocumented parameter on a metered API is the worse bet.
        assert parse_qs(mocked.last_request.query) == {
            "lat": ["4.6375"],
            "lng": ["-75.5703"],
            "bedrooms": ["3"],
            "baths": ["2"],
            "guests": ["8"],
        }

    def test_authenticates_with_the_api_key_header(
        self, http_requests_mock, salento_3br_estimate
    ):
        mocked = http_requests_mock.get(ESTIMATE_URL, json=salento_3br_estimate)

        airroi.get_revenue_estimate(
            latitude=4.6375, longitude=-75.5703, bedrooms=3, baths=2, guests=8
        )

        assert mocked.last_request.headers["x-api-key"]
        assert mocked.last_request.headers["Content-Type"] == "application/json"


class TestGetComparables:
    def test_defaults_radius_and_room_type(self, http_requests_mock):
        mocked = http_requests_mock.get(COMPARABLES_URL, json={"results": []})

        airroi.get_comparables(
            latitude=4.6375, longitude=-75.5703, bedrooms=3, baths=2.5, guests=8
        )

        query = parse_qs(mocked.last_request.query)
        assert query["radius"] == ["10"]
        # ``room_type`` filters on how the place is let, not on the building type
        # the execution plan describes.
        assert query["room_type"] == ["entire_home"]
        # Half-baths are ubiquitous and must survive the round trip.
        assert query["baths"] == ["2.5"]

    def test_overrides_are_passed_through(self, http_requests_mock):
        mocked = http_requests_mock.get(COMPARABLES_URL, json={"results": []})

        airroi.get_comparables(
            latitude=4.6375,
            longitude=-75.5703,
            bedrooms=3,
            baths=2,
            guests=8,
            radius=25,
            room_type="private_room",
        )

        query = parse_qs(mocked.last_request.query)
        assert query["radius"] == ["25"]
        assert query["room_type"] == ["private_room"]


class TestGetMarketSummary:
    def test_sends_the_market_tuple_in_native_currency(
        self, http_requests_mock, salento_market
    ):
        mocked = http_requests_mock.post(MARKET_SUMMARY_URL, json={"revenue": 1})

        airroi.get_market_summary(salento_market)

        # ``district`` is deliberately absent - AirROI matches on the three-part
        # tuple and a fourth key narrows nothing.
        assert mocked.last_request.json() == {
            "market": {
                "country": "Colombia",
                "region": "Quindío",
                "locality": "Salento",
            },
            "num_months": 12,
            "currency": "native",
        }


class TestSearchListingsByMarket:
    def test_sends_the_filter_sort_and_pagination_block(
        self, http_requests_mock, salento_market
    ):
        mocked = http_requests_mock.post(SEARCH_MARKET_URL, json={"results": []})

        airroi.search_listings_by_market(salento_market, offset=0)

        body = mocked.last_request.json()
        assert body["filter"] == {
            "room_type": {"eq": "entire_home"},
            "bedrooms": {"range": [1, 3]},
        }
        assert body["sort"] == {"ttm_revenue": "desc"}
        assert body["pagination"] == {"offset": 0, "page_size": 10}
        assert body["currency"] == "native"

    def test_five_pages_step_by_records_not_pages(
        self, http_requests_mock, salento_market
    ):
        # The bug this module was extracted to fix: ``offset`` counts records, so
        # sending the page index re-requested the same listings shifted by one.
        mocked = http_requests_mock.post(SEARCH_MARKET_URL, json={"results": []})

        for page_index in range(5):
            airroi.search_listings_by_market(
                salento_market, offset=page_index * airroi.DEFAULT_PAGE_SIZE
            )

        assert [
            sent_request.json()["pagination"]["offset"]
            for sent_request in mocked.request_history
        ] == [0, 10, 20, 30, 40]

    def test_page_size_is_overridable(self, http_requests_mock, salento_market):
        mocked = http_requests_mock.post(SEARCH_MARKET_URL, json={"results": []})

        airroi.search_listings_by_market(salento_market, offset=50, page_size=25)

        assert mocked.last_request.json()["pagination"] == {
            "offset": 50,
            "page_size": 25,
        }


class TestErrorHandling:
    @pytest.mark.parametrize("status_code", [400, 404, 429, 500, 503])
    def test_http_errors_raise_airroi_error(self, http_requests_mock, status_code):
        http_requests_mock.get(ESTIMATE_URL, status_code=status_code, json={})

        with pytest.raises(AirROIError, match="failed"):
            airroi.get_revenue_estimate(
                latitude=1.0, longitude=2.0, bedrooms=1, baths=1, guests=2
            )

    def test_malformed_body_is_reported_as_malformed(self, http_requests_mock):
        # ``JSONDecodeError`` subclasses ``RequestException``, so without ordering
        # the excepts this would be reported as a transport failure.
        http_requests_mock.get(ESTIMATE_URL, status_code=200, text="not json")

        with pytest.raises(AirROIError, match="malformed"):
            airroi.get_revenue_estimate(
                latitude=1.0, longitude=2.0, bedrooms=1, baths=1, guests=2
            )

    def test_connection_failures_raise_airroi_error(self, http_requests_mock):
        # ``requests`` wraps every transport failure in its own exception
        # hierarchy, which is why ``_send`` catches ``RequestException``.
        http_requests_mock.post(
            MARKET_SUMMARY_URL, exc=requests.exceptions.ConnectTimeout
        )

        with pytest.raises(AirROIError):
            airroi.get_market_summary(MarketEntityFactory())

    def test_the_failing_url_is_named(self, http_requests_mock):
        http_requests_mock.get(COMPARABLES_URL, status_code=500, json={})

        with pytest.raises(AirROIError, match="listings/comparables"):
            airroi.get_comparables(
                latitude=1.0, longitude=2.0, bedrooms=1, baths=1, guests=2
            )
