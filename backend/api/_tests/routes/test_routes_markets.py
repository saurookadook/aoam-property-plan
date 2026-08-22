from __future__ import annotations

import pytest
from fastapi import status
from sqlalchemy.orm import Session

from _factories.listing.db import ListingDBFactory
from _factories.listing.entity import ListingEntityFactory
from _factories.listing_financial_report.db import ListingFinancialReportDBFactory
from _factories.market.db import MarketDBFactory
from _factories.market_financial_report.db import MarketFinancialReportDBFactory
from models.market.entity import MarketEntity
from models.market.facade import MarketFacade


@pytest.fixture
def market_facade(test_db_session: Session):
    return MarketFacade(db_session=test_db_session)


def _market_json(market_record, **overrides):
    """
    What a market looks like in ``/api/markets``: the entity's own fields plus
    the three read-shaped additions, all null unless the test supplied them.
    """
    return {
        **MarketEntity.model_validate(market_record).model_dump(mode="json"),
        "financial_report": None,
        "latitude": None,
        "longitude": None,
        **overrides,
    }


class TestReadMarketsListRoute:
    def test_returns_all_markets(self, test_app_client, test_db_session: Session):
        market_zipaquira = MarketDBFactory(locality="Zipaquira")
        market_bogota = MarketDBFactory(locality="Bogota")
        market_medellin = MarketDBFactory(locality="Medellin")
        test_db_session.commit()

        result = test_app_client.get("/api/markets")

        assert result.status_code == 200
        assert result.json() == {
            "data": [
                _market_json(market_bogota),
                _market_json(market_medellin),
                _market_json(market_zipaquira),
            ]
        }

    def test_returns_no_markets(self, test_app_client):
        result = test_app_client.get("/api/markets")

        assert result.status_code == 200
        assert result.json() == {"data": []}

    def test_nests_the_latest_financial_report(
        self, test_app_client, test_db_session: Session, mock_utcnow
    ):
        market = MarketDBFactory(locality="Salento")
        test_db_session.commit()

        MarketFinancialReportDBFactory(
            market_id=market.id,
            adr_cop=100_000.0,
            last_updated=mock_utcnow.replace(tzinfo=None),
        )
        newest_report = MarketFinancialReportDBFactory(
            market_id=market.id,
            adr_cop=336_288.5,
            last_updated=mock_utcnow.replace(tzinfo=None, year=2027),
        )
        test_db_session.commit()

        result = test_app_client.get("/api/markets")

        report_data = result.json()["data"][0]["financial_report"]
        assert report_data is not None
        assert report_data["id"] == str(newest_report.id)
        assert report_data["adr_cop"] == 336_288.5

    def test_includes_a_market_that_has_never_been_summarised(
        self, test_app_client, test_db_session: Session
    ):
        """
        A market with no figures is still a market. Dropping the row would hide
        it from the roster instead of showing it as incomplete.
        """
        MarketDBFactory(locality="Cartagena")
        test_db_session.commit()

        result = test_app_client.get("/api/markets")

        assert result.status_code == 200
        assert result.json()["data"][0]["financial_report"] is None

    def test_does_not_multiply_a_market_by_its_report_history(
        self, test_app_client, test_db_session: Session
    ):
        market = MarketDBFactory(locality="Pance")
        test_db_session.commit()

        for _ in range(3):
            MarketFinancialReportDBFactory(market_id=market.id)
        test_db_session.commit()

        result = test_app_client.get("/api/markets")

        assert len(result.json()["data"]) == 1

    def test_carries_the_centroid_of_the_ingested_listings(
        self, test_app_client, test_db_session: Session
    ):
        market = MarketDBFactory(locality="Salento")
        test_db_session.commit()

        for latitude, longitude in [(4.62, -75.58), (4.66, -75.54)]:
            ListingDBFactory(
                market_id=market.id,
                latitude=latitude,
                longitude=longitude,
                location=f"POINT({longitude} {latitude})",
            )
        test_db_session.commit()

        market_data = test_app_client.get("/api/markets").json()["data"][0]

        assert market_data["latitude"] == pytest.approx(4.64, abs=1e-5)
        assert market_data["longitude"] == pytest.approx(-75.56, abs=1e-5)

    def test_market_with_nothing_ingested_has_no_coordinates(
        self, test_app_client, test_db_session: Session
    ):
        MarketDBFactory(locality="Bogota")
        test_db_session.commit()

        market_data = test_app_client.get("/api/markets").json()["data"][0]

        assert market_data["latitude"] is None
        assert market_data["longitude"] is None


class TestReadMarketOverviewRoute:
    def test_returns_market_and_listings(
        self, test_app_client, test_db_session: Session
    ):
        market = MarketDBFactory()
        test_db_session.commit()

        listings = [ListingEntityFactory(market_id=market.id) for _ in range(2)]
        for listing in listings:
            ListingDBFactory(**listing.model_dump())
        test_db_session.commit()

        result = test_app_client.get(f"/api/markets/{market.id}")

        assert result.status_code == 200
        assert result.json()["data"]["market"] == MarketEntity.model_validate(
            market
        ).model_dump(mode="json")
        # NOTE: compared by ``airroi_id`` rather than by dumping the entities,
        # because ``include_financial_reports=True`` rebuilds ``location`` from
        # the stored coordinates instead of reading it back through
        # ``ST_AsText`` - see ``ListingFacade._build_select_clause``.
        assert [
            listing["airroi_id"] for listing in result.json()["data"]["listings"]
        ] == sorted(listing.airroi_id for listing in listings)

    def test_returns_market_but_no_listings(
        self, test_app_client, test_db_session: Session
    ):
        market = MarketDBFactory()
        test_db_session.commit()

        result = test_app_client.get(f"/api/markets/{market.id}")

        assert result.status_code == 200
        assert result.json() == {
            "data": {
                "market": MarketEntity.model_validate(market).model_dump(mode="json"),
                "listings": [],
            }
        }

    def test_includes_listing_financial_reports(
        self, test_app_client, test_db_session: Session
    ):
        """
        The overview now eager-loads each listing's reports. Without them the
        market screen would issue one query per listing to render its figures.
        """
        market = MarketDBFactory()
        test_db_session.commit()

        listing = ListingEntityFactory(market_id=market.id)
        listing_record = ListingDBFactory(**listing.model_dump())
        test_db_session.commit()

        report = ListingFinancialReportDBFactory(listing_id=listing_record.id)
        test_db_session.commit()

        result = test_app_client.get(f"/api/markets/{market.id}")

        assert result.status_code == 200
        listings_data = result.json()["data"]["listings"]
        assert len(listings_data) == 1
        assert [
            item["id"] for item in listings_data[0]["listing_financial_reports"]
        ] == [str(report.id)]

    def test_raises_http_exception_for_nonexistent_market(
        self, test_app_client, test_db_session: Session
    ):
        non_existent_market_id = "01d336ff-c742-4682-80bb-5f7d5cdf8d26"

        result = test_app_client.get(f"/api/markets/{non_existent_market_id}")
        assert result.status_code == status.HTTP_404_NOT_FOUND
        assert result.json() == {"detail": "Market not found"}


class TestReadMarketOverviewRouteQueryParams:
    """
    ``bedrooms``, ``property_type``, ``sort`` and ``limit`` are applied in the
    query, not to the fetched list - see ``ListingFacade.get_all_by_market_id``.
    """

    @pytest.fixture
    def market(self, test_db_session: Session):
        market_record = MarketDBFactory()
        test_db_session.commit()
        return market_record

    def _ingest(self, market, test_db_session, **kwargs):
        # ``ListingDBFactory.location`` is a faker tuple, not WKT, so every
        # caller has to supply a real point.
        latitude = kwargs.pop("latitude", 4.64)
        longitude = kwargs.pop("longitude", -75.56)
        listing = ListingDBFactory(
            market_id=market.id,
            latitude=latitude,
            longitude=longitude,
            location=f"POINT({longitude} {latitude})",
            **kwargs,
        )
        test_db_session.commit()
        return listing

    def _airroi_ids(self, result):
        return [listing["airroi_id"] for listing in result.json()["data"]["listings"]]

    def test_defaults_to_airroi_id_ascending(
        self, test_app_client, market, test_db_session
    ):
        for airroi_id in [300, 100, 200]:
            self._ingest(market, test_db_session, airroi_id=airroi_id)

        result = test_app_client.get(f"/api/markets/{market.id}")

        assert self._airroi_ids(result) == [100, 200, 300]

    def test_filters_by_bedrooms(self, test_app_client, market, test_db_session):
        self._ingest(market, test_db_session, airroi_id=100, bedrooms=2)
        self._ingest(market, test_db_session, airroi_id=200, bedrooms=3)

        result = test_app_client.get(f"/api/markets/{market.id}?bedrooms=3")

        assert self._airroi_ids(result) == [200]

    def test_filters_by_property_type(self, test_app_client, market, test_db_session):
        self._ingest(market, test_db_session, airroi_id=100, property_type="Cabin")
        self._ingest(market, test_db_session, airroi_id=200, property_type="Apartment")

        result = test_app_client.get(f"/api/markets/{market.id}?property_type=Cabin")

        assert self._airroi_ids(result) == [100]

    def test_combines_filters(self, test_app_client, market, test_db_session):
        self._ingest(
            market, test_db_session, airroi_id=100, bedrooms=3, property_type="Cabin"
        )
        self._ingest(
            market, test_db_session, airroi_id=200, bedrooms=3, property_type="House"
        )
        self._ingest(
            market, test_db_session, airroi_id=300, bedrooms=2, property_type="Cabin"
        )

        result = test_app_client.get(
            f"/api/markets/{market.id}?bedrooms=3&property_type=Cabin"
        )

        assert self._airroi_ids(result) == [100]

    def test_limits_in_the_query(self, test_app_client, market, test_db_session):
        for airroi_id in [100, 200, 300]:
            self._ingest(market, test_db_session, airroi_id=airroi_id)

        result = test_app_client.get(f"/api/markets/{market.id}?limit=2")

        assert self._airroi_ids(result) == [100, 200]

    def test_sorts_by_revenue(self, test_app_client, market, test_db_session):
        quiet = self._ingest(market, test_db_session, airroi_id=100)
        busy = self._ingest(market, test_db_session, airroi_id=200)

        ListingFinancialReportDBFactory(listing_id=quiet.id, ttm_revenue=1_000_000.0)
        ListingFinancialReportDBFactory(listing_id=busy.id, ttm_revenue=90_000_000.0)
        test_db_session.commit()

        result = test_app_client.get(f"/api/markets/{market.id}?sort=revenue")

        assert self._airroi_ids(result) == [200, 100]

    def test_sorts_by_occupancy(self, test_app_client, market, test_db_session):
        quiet = self._ingest(market, test_db_session, airroi_id=100)
        busy = self._ingest(market, test_db_session, airroi_id=200)

        ListingFinancialReportDBFactory(listing_id=quiet.id, ttm_occupancy_rate=0.12)
        ListingFinancialReportDBFactory(listing_id=busy.id, ttm_occupancy_rate=0.87)
        test_db_session.commit()

        result = test_app_client.get(f"/api/markets/{market.id}?sort=occupancy")

        assert self._airroi_ids(result) == [200, 100]

    def test_sorting_does_not_duplicate_a_listing_with_several_reports(
        self, test_app_client, market, test_db_session
    ):
        """
        ``listing_financial_reports`` is a child table with potentially many rows
        per listing, so the sort goes through a ``LATERAL ... LIMIT 1``. A plain
        join would return this listing three times.
        """
        listing = self._ingest(market, test_db_session, airroi_id=100)

        for revenue in [1_000_000.0, 2_000_000.0, 3_000_000.0]:
            ListingFinancialReportDBFactory(listing_id=listing.id, ttm_revenue=revenue)
        test_db_session.commit()

        result = test_app_client.get(f"/api/markets/{market.id}?sort=revenue")

        assert self._airroi_ids(result) == [100]

    def test_sorting_puts_listings_without_a_report_last(
        self, test_app_client, market, test_db_session
    ):
        self._ingest(market, test_db_session, airroi_id=100)
        reported = self._ingest(market, test_db_session, airroi_id=200)

        ListingFinancialReportDBFactory(listing_id=reported.id, ttm_revenue=5_000_000.0)
        test_db_session.commit()

        result = test_app_client.get(f"/api/markets/{market.id}?sort=revenue")

        assert self._airroi_ids(result) == [200, 100]

    def test_sort_and_limit_together_take_the_top_of_the_market(
        self, test_app_client, market, test_db_session
    ):
        for airroi_id, revenue in [(100, 1.0), (200, 9.0), (300, 5.0)]:
            listing = self._ingest(market, test_db_session, airroi_id=airroi_id)
            ListingFinancialReportDBFactory(
                listing_id=listing.id, ttm_revenue=revenue * 1_000_000
            )
        test_db_session.commit()

        result = test_app_client.get(f"/api/markets/{market.id}?sort=revenue&limit=2")

        assert self._airroi_ids(result) == [200, 300]

    @pytest.mark.parametrize(
        "query_string",
        [
            "sort=price",
            "limit=0",
            "limit=201",
            "bedrooms=-1",
            "bedrooms=three",
        ],
    )
    def test_rejects_invalid_params(self, query_string, test_app_client, market):
        result = test_app_client.get(f"/api/markets/{market.id}?{query_string}")

        assert result.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_ignores_another_markets_listings(
        self, test_app_client, market, test_db_session
    ):
        other_market = MarketDBFactory(locality="Somewhere Else")
        test_db_session.commit()

        self._ingest(market, test_db_session, airroi_id=100)
        self._ingest(other_market, test_db_session, airroi_id=200)

        result = test_app_client.get(f"/api/markets/{market.id}?sort=revenue")

        assert self._airroi_ids(result) == [100]
