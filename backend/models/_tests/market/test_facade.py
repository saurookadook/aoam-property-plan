from __future__ import annotations

import pytest

from _factories.listing.db import ListingDBFactory
from _factories.market.db import MarketDBFactory
from models.market.entity import MarketEntity
from models.market.facade import MarketFacade


class TestMarketFacade:
    @pytest.fixture
    def market_facade(self, test_db_session):
        return MarketFacade(db_session=test_db_session)

    @pytest.fixture
    def market_record(self, expected_market_dict, test_db_session):
        market = MarketDBFactory(**expected_market_dict)
        test_db_session.commit()
        return market

    def _compare_result_with_expected(self, result: MarketEntity, expected_dict: dict):
        for key, value in expected_dict.items():
            assert getattr(result, key) == value

        return True

    def test_get_one_by_id(self, market_facade, market_record):
        result = market_facade.get_one_by_id(market_record.id)
        assert result == MarketEntity.model_validate(market_record)

    def test_get_one_by_id_no_result(self, market_facade):
        with pytest.raises(MarketFacade.NoResultFound):
            non_existent_id = "988d0b5d-d4a5-4808-a94d-2d9df1df7588"
            market_facade.get_one_by_id(non_existent_id)

    def test_get_all(self, market_facade, market_record, test_db_session):
        market_2 = MarketDBFactory(locality="Bogotá")
        market_3 = MarketDBFactory(locality="Medellín")
        test_db_session.commit()

        result = market_facade.get_all()
        expected = [
            MarketEntity.model_validate(market_2),
            MarketEntity.model_validate(market_3),
            MarketEntity.model_validate(market_record),
        ]

        assert result == expected

    def test_create_or_update_creates_new_record(
        self, market_facade, expected_market_dict
    ):
        result = market_facade.create_or_update(payload=expected_market_dict)

        assert self._compare_result_with_expected(result, expected_market_dict)

    def test_create_or_update_updates_existing_record(
        self,
        market_facade,
        market_record,
    ):
        market_entity = MarketEntity.model_validate(market_record)
        market_record_dict = market_entity.model_dump()
        updated_payload = {
            **market_record_dict,
            "region": "Updated Region",
        }

        result = market_facade.create_or_update(payload=updated_payload)

        assert self._compare_result_with_expected(result, updated_payload)
        assert result.region != market_record_dict["region"]


class TestMarketFacadeCentroids:
    """
    A market's position is an average over its ingested listings, computed in the
    query rather than stored - see ``MarketCentroidEntity``.
    """

    @pytest.fixture
    def market_facade(self, test_db_session):
        return MarketFacade(db_session=test_db_session)

    @pytest.fixture
    def market_record(self, expected_market_dict, test_db_session):
        market = MarketDBFactory(**expected_market_dict)
        test_db_session.commit()
        return market

    def _ingest(self, market_id, points, test_db_session):
        for latitude, longitude in points:
            ListingDBFactory(
                market_id=market_id,
                latitude=latitude,
                longitude=longitude,
                location=f"POINT({longitude} {latitude})",
            )
        test_db_session.commit()

    def test_averages_the_ingested_listings(
        self, market_facade, market_record, test_db_session
    ):
        self._ingest(
            market_record.id,
            [(4.62, -75.58), (4.64, -75.56), (4.66, -75.54)],
            test_db_session,
        )

        centroid = market_facade.get_centroid_by_id(market_record.id)

        assert centroid is not None
        assert centroid.market_id == market_record.id
        assert centroid.latitude == pytest.approx(4.64, abs=1e-5)
        assert centroid.longitude == pytest.approx(-75.56, abs=1e-5)
        assert centroid.listing_count == 3

    def test_counts_ingested_listings_not_the_markets_own_listing_count(
        self,
        market_facade,
        market_record,
        test_market_financial_report_record,
        test_db_session,
    ):
        """
        ``listing_count`` on a centroid is how much of a market we hold;
        ``market_financial_reports.listing_count`` is AirROI's count for the whole
        market. The fixture report claims ten and only two are ingested.
        """
        self._ingest(
            market_record.id, [(4.62, -75.58), (4.66, -75.54)], test_db_session
        )

        centroid = market_facade.get_centroid_by_id(market_record.id)

        assert test_market_financial_report_record.listing_count == 10.0
        assert centroid is not None
        assert centroid.listing_count == 2

    def test_no_centroid_for_a_market_with_nothing_ingested(
        self, market_facade, market_record
    ):
        assert market_facade.get_centroid_by_id(market_record.id) is None

    def test_no_centroid_for_an_unknown_market(self, market_facade):
        # Deliberately not a raise: "no such market" and "nothing ingested yet"
        # are the same answer to the only question the caller is asking.
        assert (
            market_facade.get_centroid_by_id("988d0b5d-d4a5-4808-a94d-2d9df1df7588")
            is None
        )

    def test_ignores_another_markets_listings(
        self, market_facade, market_record, test_db_session
    ):
        other_market = MarketDBFactory(locality="Somewhere Else")
        test_db_session.commit()

        self._ingest(market_record.id, [(4.64, -75.56)], test_db_session)
        self._ingest(other_market.id, [(10.40, -75.51)], test_db_session)

        centroid = market_facade.get_centroid_by_id(market_record.id)

        assert centroid is not None
        assert centroid.latitude == pytest.approx(4.64, abs=1e-5)
        assert centroid.listing_count == 1

    def test_get_all_centroids_returns_one_per_ingested_market(
        self, market_facade, market_record, test_db_session
    ):
        other_market = MarketDBFactory(locality="Somewhere Else")
        empty_market = MarketDBFactory(locality="Nothing Ingested")
        test_db_session.commit()

        self._ingest(
            market_record.id, [(4.62, -75.58), (4.66, -75.54)], test_db_session
        )
        self._ingest(other_market.id, [(10.40, -75.51)], test_db_session)

        centroids = market_facade.get_all_centroids()
        by_market = {centroid.market_id: centroid for centroid in centroids}

        # A market with nothing ingested is absent rather than present with a
        # null point - there is no position to report.
        assert empty_market.id not in by_market
        assert set(by_market) == {market_record.id, other_market.id}
        assert by_market[market_record.id].latitude == pytest.approx(4.64, abs=1e-5)
        assert by_market[market_record.id].listing_count == 2
        assert by_market[other_market.id].listing_count == 1

    def test_get_all_centroids_is_empty_with_nothing_ingested(
        self, market_facade, market_record
    ):
        assert market_facade.get_all_centroids() == []
