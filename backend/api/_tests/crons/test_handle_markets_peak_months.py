from __future__ import annotations

import pytest

from _factories.listing.db import ListingDBFactory
from _factories.market.db import MarketDBFactory
from _factories.market_financial_report.db import MarketFinancialReportDBFactory
from api.crons.handlers import handle_markets_peak_months
from constants import AIRROI_BASE_URL
from models.market_financial_report.facade import MarketFinancialReportFacade

ESTIMATE_URL = f"{AIRROI_BASE_URL}/calculator/estimate"

# The coordinates the Salento capture was taken at - the centroid of the
# listings below lands on them, so the dynamic mock can find it.
SALENTO = (4.6375, -75.5703)


@pytest.fixture
def salento_market(test_db_session):
    market = MarketDBFactory(
        country="Colombia", region="Quindío", locality="Salento", district=None
    )
    test_db_session.commit()
    return market


@pytest.fixture
def market_listings(salento_market, test_db_session):
    latitude, longitude = SALENTO

    test_listings_details = (
        (latitude - 0.01, longitude - 0.002, 2, 1.0),
        (latitude, longitude, 3, 2.0),
        (latitude + 0.01, longitude + 0.002, 3, 2.5),
    )
    """
    Three listings whose mean position is the capture's coordinates and
    whose median size is 3 bedrooms / 2 baths.
    """

    listings = []

    for listing_latitude, listing_longitude, bedrooms, baths in test_listings_details:
        listings.append(
            ListingDBFactory(
                market_id=salento_market.id,
                latitude=listing_latitude,
                longitude=listing_longitude,
                location=f"POINT({listing_longitude} {listing_latitude})",
                bedrooms=bedrooms,
                baths=baths,
            )
        )

    test_db_session.commit()
    return listings


@pytest.fixture
def latest_report(salento_market, test_db_session):
    report = MarketFinancialReportDBFactory(
        market_id=salento_market.id,
        monthly_revenue_distribution=None,
        peak_months=None,
    )
    test_db_session.commit()
    # Read before the handler detaches it by removing the scoped session.
    return report.id


# ``monthly_revenue_distributions`` from
# ``_research/calculator/estimate/salento_quindio_colombia__2-baths_3-bedrooms_8-guests.json``
# - the capture the median 3-bedroom centroid query resolves to.
SALENTO_DISTRIBUTION = [
    0.09494533694086553,
    0.07502271701425754,
    0.08286931348819382,
    0.08220289734011337,
    0.07287337677798432,
    0.07819997404771865,
    0.0988698349470266,
    0.08618993161190687,
    0.06902114243349175,
    0.07618002102302641,
    0.07739341926374922,
    0.10623203511166586,
]


class TestHandleMarketsPeakMonths:
    def test_writes_the_top_three_months_to_the_latest_report(
        self,
        airroi_estimate_mock,
        latest_report,
        market_listings,
        salento_market,
        test_db_session,
    ):
        handle_markets_peak_months()

        refreshed = MarketFinancialReportFacade(
            db_session=test_db_session
        ).get_one_by_id(latest_report)

        # The only route to this column: ``/markets/summary`` has never returned
        # ``peak_months`` and there is no ``/markets/seasonality`` endpoint.
        assert refreshed.peak_months == ["December", "July", "January"]

    def test_stores_the_distribution_the_month_names_came_from(
        self,
        airroi_estimate_mock,
        latest_report,
        market_listings,
        salento_market,
        test_db_session,
    ):
        """
        The twelve numbers, not just the three names derived from them. The handler
        already fetched them; discarding them left a market-level seasonality view
        with nothing to draw.
        """
        handle_markets_peak_months()

        refreshed = MarketFinancialReportFacade(
            db_session=test_db_session
        ).get_one_by_id(latest_report)

        assert refreshed.monthly_revenue_distribution is not None
        assert len(refreshed.monthly_revenue_distribution) == 12
        # The column is ``REAL[]``, so the stored values are float32 rounded off
        # the float64 the response carried.
        assert refreshed.monthly_revenue_distribution == pytest.approx(
            SALENTO_DISTRIBUTION, rel=1e-6
        )
        assert sum(refreshed.monthly_revenue_distribution) == pytest.approx(1.0)

    def test_asks_about_the_centroid_and_the_median_property(
        self,
        airroi_estimate_mock,
        latest_report,
        market_listings,
        salento_market,
    ):
        handle_markets_peak_months()

        query = airroi_estimate_mock.last_request.qs
        assert float(query["lat"][0]) == pytest.approx(SALENTO[0], abs=1e-6)
        assert float(query["lng"][0]) == pytest.approx(SALENTO[1], abs=1e-6)
        assert query["bedrooms"] == ["3"]
        assert query["baths"] == ["2.0"]
        # ``listings`` has no ``guests`` column, so it falls back to the same
        # two-per-bedroom assumption a property analysis makes.
        assert query["guests"] == ["6"]

    def test_skips_a_market_that_has_never_been_summarised(
        self, airroi_estimate_mock, market_listings, salento_market
    ):
        handle_markets_peak_months()

        assert airroi_estimate_mock.call_count == 0

    def test_skips_a_market_with_no_ingested_listings(
        self, airroi_estimate_mock, latest_report, salento_market
    ):
        handle_markets_peak_months()

        assert airroi_estimate_mock.call_count == 0

    def test_skips_a_market_whose_listings_report_no_bath_count(
        self, airroi_estimate_mock, latest_report, salento_market, test_db_session
    ):
        latitude, longitude = SALENTO
        ListingDBFactory(
            market_id=salento_market.id,
            latitude=latitude,
            longitude=longitude,
            location=f"POINT({longitude} {latitude})",
            bedrooms=3,
            baths=None,
        )
        test_db_session.commit()

        handle_markets_peak_months()

        # A fabricated bath count silently changes which comps come back, so the
        # market is skipped rather than guessed at.
        assert airroi_estimate_mock.call_count == 0

    def test_an_airroi_failure_leaves_the_report_untouched(
        self,
        http_requests_mock,
        latest_report,
        market_listings,
        salento_market,
        test_db_session,
    ):
        http_requests_mock.get(ESTIMATE_URL, status_code=500, json={})

        handle_markets_peak_months()

        refreshed = MarketFinancialReportFacade(
            db_session=test_db_session
        ).get_one_by_id(latest_report)

        assert refreshed.peak_months is None
        assert refreshed.monthly_revenue_distribution is None
