from __future__ import annotations

from collections import deque
from datetime import date, datetime, timezone
from uuid import UUID

import pytest

from _factories.listing.db import ListingDBFactory
from _factories.listing.entity import ListingEntityFactory
from _factories.listing_financial_report.db import ListingFinancialReportDBFactory
from _factories.market.db import MarketDBFactory
from _factories.market.entity import MarketEntityFactory
from models.listing.entity import ListingEntity, NewestListingEntity
from models.listing.facade import ListingFacade
from models.listing_financial_report.entity import ListingFinancialReportEntity
from models.market.facade import MarketFacade


class TestListingFacade:
    @pytest.fixture
    def listing_facade(self, test_db_session):
        return ListingFacade(db_session=test_db_session)

    @pytest.fixture
    def listing_record(self, expected_listing_dict, test_db_session):
        listing = ListingDBFactory(**expected_listing_dict)
        test_db_session.commit()
        return listing

    def test_get_one_by_id(self, listing_facade, listing_record, expected_listing_dict):
        result = listing_facade.get_one_by_id(listing_record.id)

        assert self._compare_result_with_expected(result, expected_listing_dict)

    def test_get_one_by_id_no_result(self, listing_facade):
        with pytest.raises(ListingFacade.NoResultFound):
            non_existent_id = UUID("988d0b5d-d4a5-4808-a94d-2d9df1df7588")
            listing_facade.get_one_by_id(non_existent_id)

    def test_get_one_by_id_includes_financial_reports(
        self, listing_facade, listing_record, expected_listing_dict, test_db_session
    ):
        financial_report_records = [
            ListingFinancialReportDBFactory(listing_id=listing_record.id)
            for _ in range(2)
        ]
        test_db_session.commit()

        result = listing_facade.get_one_by_id(
            listing_record.id, include_financial_reports=True
        )

        assert self._compare_result_with_expected(result, expected_listing_dict)
        assert len(result.listing_financial_reports) == 2
        expected_reports = [
            ListingFinancialReportEntity.model_validate(record)
            for record in financial_report_records
        ]
        assert sorted(result.listing_financial_reports, key=lambda r: r.id) == sorted(
            expected_reports, key=lambda r: r.id
        )

    def test_get_one_by_id_no_financial_reports_by_default(
        self, listing_facade, listing_record, test_db_session
    ):
        ListingFinancialReportDBFactory(listing_id=listing_record.id)
        test_db_session.commit()

        result = listing_facade.get_one_by_id(listing_record.id)

        assert result.listing_financial_reports == []

    def test_get_one_by_airroi_id(
        self, listing_facade, listing_record, expected_listing_dict
    ):
        result = listing_facade.get_one_by_airroi_id(listing_record.airroi_id)

        assert self._compare_result_with_expected(result, expected_listing_dict)

    def test_get_one_by_airroi_id_no_result(self, listing_facade):
        with pytest.raises(ListingFacade.NoResultFound):
            non_existent_airroi_id = 9999999
            listing_facade.get_one_by_airroi_id(non_existent_airroi_id)

    def test_get_one_by_airroi_id_includes_financial_reports(
        self, listing_facade, listing_record, expected_listing_dict, test_db_session
    ):
        financial_report_records = [
            ListingFinancialReportDBFactory(listing_id=listing_record.id)
            for _ in range(2)
        ]
        test_db_session.commit()

        result = listing_facade.get_one_by_airroi_id(
            listing_record.airroi_id, include_financial_reports=True
        )

        assert self._compare_result_with_expected(result, expected_listing_dict)
        assert len(result.listing_financial_reports) == 2
        expected_reports = [
            ListingFinancialReportEntity.model_validate(record)
            for record in financial_report_records
        ]
        assert sorted(result.listing_financial_reports, key=lambda r: r.id) == sorted(
            expected_reports, key=lambda r: r.id
        )

    def test_get_one_by_airroi_id_no_financial_reports_by_default(
        self, listing_facade, listing_record, test_db_session
    ):
        ListingFinancialReportDBFactory(listing_id=listing_record.id)
        test_db_session.commit()

        result = listing_facade.get_one_by_airroi_id(listing_record.airroi_id)

        assert result.listing_financial_reports == []

    def test_get_all_by_market_id(self, listing_facade: ListingFacade, test_db_session):
        expected_market = MarketEntityFactory()
        MarketDBFactory(**expected_market.model_dump())
        test_db_session.commit()

        expected_listings: list[ListingEntity] = []
        for _ in range(3):
            listing = ListingEntityFactory(market_id=expected_market.id)
            ListingDBFactory(**listing.model_dump())
            expected_listings.append(listing)
        test_db_session.commit()

        results = listing_facade.get_all_by_market_id(expected_market.id)

        assert len(results) == 3
        for listing_result in results:
            expected_listing = next(
                (e_l for e_l in expected_listings if e_l.id == listing_result.id), None
            )
            assert expected_listing is not None
            assert expected_listing.model_dump() == listing_result.model_dump()

    def test_get_all_by_market_id_no_results(self, listing_facade, test_db_session):
        expected_market = MarketEntityFactory()
        MarketDBFactory(**expected_market.model_dump())
        test_db_session.commit()

        results = listing_facade.get_all_by_market_id(expected_market.id)

        assert results == []

    def test_get_all_by_market_id_no_market(self, listing_facade):
        non_existent_market_id = "01d336ff-c742-4682-80bb-5f7d5cdf8d26"

        with pytest.raises(MarketFacade.NoResultFound):
            listing_facade.get_all_by_market_id(non_existent_market_id)

    def test_get_newest(self, listing_facade: ListingFacade, test_db_session):
        expected_market = MarketEntityFactory()
        other_market = MarketEntityFactory()
        MarketDBFactory(**expected_market.model_dump())
        MarketDBFactory(**other_market.model_dump())
        test_db_session.commit()

        today = date.today()
        today_now = datetime(
            year=today.year,
            month=today.month,
            day=today.day,
            hour=13,
            minute=30,
            tzinfo=timezone.utc,
        )

        expected_listings: deque[ListingEntity] = deque()
        for i in range(10):
            market_id = None

            if i % 2 == 0:
                market_id = expected_market.id
            if i % 3 == 0:
                market_id = other_market.id

            listing = ListingEntityFactory(
                created_at=today_now.replace(minute=today_now.minute + i, second=i),
                market_id=market_id,
                updated_at=today_now.replace(
                    minute=today_now.minute + i + 1, second=1 + i
                ),
            )
            ListingDBFactory(**listing.model_dump())

            if (i % 2 == 0 or i % 3 == 0) and listing.market_id is not None:
                expected_listings.appendleft(listing)
            if len(expected_listings) > 5:
                expected_listings.pop()
        test_db_session.commit()

        results = listing_facade.get_newest()

        assert len(results) == 5
        for expected_listing, listing_result in zip(expected_listings, results):
            assert expected_listing is not None
            assert expected_listing.cover_photo_url == listing_result.cover_photo_url
            assert expected_listing.created_at == listing_result.created_at
            assert expected_listing.id == listing_result.id
            assert expected_listing.market_id == listing_result.market_id
            assert expected_listing.name == listing_result.name
            assert expected_listing.updated_at == listing_result.updated_at

    def test_create_or_update_creates_new_record(
        self, listing_facade, expected_listing_dict
    ):
        result = listing_facade.create_or_update(payload=expected_listing_dict)

        assert self._compare_result_with_expected(result, expected_listing_dict)

    def test_create_or_update_creates_new_record_no_id(
        self, listing_facade, expected_listing_dict
    ):
        del expected_listing_dict["id"]
        result = listing_facade.create_or_update(payload=expected_listing_dict)

        assert self._compare_result_with_expected(result, expected_listing_dict)

    def test_create_or_update_updates_existing_record(
        self, listing_facade, listing_record, expected_listing_dict
    ):
        updated_payload = {
            **expected_listing_dict,
            "id": listing_record.id,
            "airroi_id": listing_record.airroi_id,
            "bedrooms": expected_listing_dict["bedrooms"] + 1,
        }

        result = listing_facade.create_or_update(payload=updated_payload)

        assert self._compare_result_with_expected(result, updated_payload)
        assert result.bedrooms != expected_listing_dict["bedrooms"]

    def _compare_result_with_expected(self, result: ListingEntity, expected_dict: dict):
        for key, value in expected_dict.items():
            assert getattr(result, key) == value

        return True


class TestListingFacadeMarketQueryParams:
    """
    ``get_all_by_market_id`` pushes filtering, sorting and limiting into the
    query. Fetching every listing and slicing in Python would make ``limit``
    cosmetic and would make ``sort`` describe the page rather than the market.
    """

    @pytest.fixture
    def listing_facade(self, test_db_session):
        return ListingFacade(db_session=test_db_session)

    @pytest.fixture
    def market_record(self, test_db_session):
        market = MarketDBFactory()
        test_db_session.commit()
        return market

    def _ingest(self, market_record, test_db_session, **kwargs):
        latitude = kwargs.pop("latitude", 4.64)
        longitude = kwargs.pop("longitude", -75.56)
        listing = ListingDBFactory(
            market_id=market_record.id,
            latitude=latitude,
            longitude=longitude,
            location=f"POINT({longitude} {latitude})",
            **kwargs,
        )
        test_db_session.commit()
        return listing

    def test_defaults_to_airroi_id_ascending(
        self, listing_facade, market_record, test_db_session
    ):
        for airroi_id in [300, 100, 200]:
            self._ingest(market_record, test_db_session, airroi_id=airroi_id)

        results = listing_facade.get_all_by_market_id(market_record.id)

        assert [listing.airroi_id for listing in results] == [100, 200, 300]

    def test_filters_and_limits(self, listing_facade, market_record, test_db_session):
        self._ingest(market_record, test_db_session, airroi_id=100, bedrooms=3)
        self._ingest(market_record, test_db_session, airroi_id=200, bedrooms=3)
        self._ingest(market_record, test_db_session, airroi_id=300, bedrooms=2)

        results = listing_facade.get_all_by_market_id(
            market_record.id, bedrooms=3, limit=1
        )

        assert [listing.airroi_id for listing in results] == [100]

    def test_sort_reaches_the_latest_financial_report(
        self, listing_facade, market_record, test_db_session
    ):
        listing = self._ingest(market_record, test_db_session, airroi_id=100)
        other = self._ingest(market_record, test_db_session, airroi_id=200)

        ListingFinancialReportDBFactory(listing_id=listing.id, ttm_revenue=1.0)
        ListingFinancialReportDBFactory(listing_id=other.id, ttm_revenue=2.0)
        test_db_session.commit()

        results = listing_facade.get_all_by_market_id(market_record.id, sort="revenue")

        assert [listing.airroi_id for listing in results] == [200, 100]

    def test_rejects_an_unknown_sort(
        self, listing_facade, market_record, test_db_session
    ):
        # The route constrains ``sort`` with a ``Literal`` so this is a 422 over
        # HTTP, but the facade is callable from crons and scripts too.
        with pytest.raises(ValueError, match="Unknown listing sort 'price'"):
            listing_facade.get_all_by_market_id(market_record.id, sort="price")

    def test_includes_financial_reports_on_request(
        self, listing_facade, market_record, test_db_session
    ):
        listing = self._ingest(market_record, test_db_session, airroi_id=100)
        report = ListingFinancialReportDBFactory(listing_id=listing.id)
        test_db_session.commit()

        results = listing_facade.get_all_by_market_id(
            market_record.id, include_financial_reports=True
        )

        assert len(results) == 1
        assert [item.id for item in results[0].listing_financial_reports] == [report.id]

    def test_excludes_financial_reports_by_default(
        self, listing_facade, market_record, test_db_session
    ):
        listing = self._ingest(market_record, test_db_session, airroi_id=100)
        ListingFinancialReportDBFactory(listing_id=listing.id)
        test_db_session.commit()

        results = listing_facade.get_all_by_market_id(market_record.id)

        assert results[0].listing_financial_reports == []

    def test_sorting_with_reports_does_not_duplicate_a_listing(
        self, listing_facade, market_record, test_db_session
    ):
        listing = self._ingest(market_record, test_db_session, airroi_id=100)

        for revenue in [1.0, 2.0, 3.0]:
            ListingFinancialReportDBFactory(listing_id=listing.id, ttm_revenue=revenue)
        test_db_session.commit()

        results = listing_facade.get_all_by_market_id(
            market_record.id, sort="revenue", include_financial_reports=True
        )

        assert [listing.airroi_id for listing in results] == [100]
        assert len(results[0].listing_financial_reports) == 3
