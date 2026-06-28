from __future__ import annotations

import pytest

from _factories.listing.db import ListingDBFactory
from _factories.listing_financial_report.db import ListingFinancialReportDBFactory
from models.listing_financial_report.entity import ListingFinancialReportEntity
from models.listing_financial_report.facade import ListingFinancialReportFacade


class TestListingFinancialReportFacade:
    @pytest.fixture
    def listing_financial_report_facade(self, test_db_session):
        return ListingFinancialReportFacade(db_session=test_db_session)

    @pytest.fixture
    def listing_record(self, expected_listing_dict, test_db_session):
        listing = ListingDBFactory(**expected_listing_dict)
        test_db_session.commit()
        return listing

    @pytest.fixture
    def listing_financial_report_record(
        self,
        listing_record,
        expected_listing_financial_report_dict,
        test_db_session,
    ):
        listing_financial_report = ListingFinancialReportDBFactory(
            **expected_listing_financial_report_dict
        )
        test_db_session.commit()
        return listing_financial_report

    def _compare_result_with_expected(
        self,
        result: ListingFinancialReportEntity,
        expected_dict: dict,
    ):
        for key, value in expected_dict.items():
            assert getattr(result, key) == value

        return True

    def test_get_one_by_id(
        self,
        listing_financial_report_facade,
        listing_financial_report_record,
    ):
        result = listing_financial_report_facade.get_one_by_id(
            listing_financial_report_record.id
        )
        assert result == ListingFinancialReportEntity.model_validate(
            listing_financial_report_record
        )

    def test_get_one_by_id_no_result(self, listing_financial_report_facade):
        with pytest.raises(ListingFinancialReportFacade.NoResultFound):
            non_existent_id = "988d0b5d-d4a5-4808-a94d-2d9df1df7588"
            listing_financial_report_facade.get_one_by_id(non_existent_id)

    def test_get_all_by_listing_id(
        self,
        expected_listing_financial_report_dict,
        listing_financial_report_facade,
        listing_financial_report_record,
        test_db_session,
    ):
        for _ in range(2):
            ListingFinancialReportDBFactory(
                listing_id=expected_listing_financial_report_dict["listing_id"]
            )
        test_db_session.commit()

        result = listing_financial_report_facade.get_all_by_listing_id(
            listing_financial_report_record.listing_id
        )
        assert len(result) == 3

    def test_get_all_by_listing_id_no_result(self, listing_financial_report_facade):
        non_existent_id = "988d0b5d-d4a5-4808-a94d-2d9df1df7588"
        results = listing_financial_report_facade.get_all_by_listing_id(non_existent_id)
        assert results == []

    def has_one_by_listing_id_for_date_true(
        self,
        listing_financial_report_facade,
        listing_financial_report_record,
        test_db_session,
    ):
        result = listing_financial_report_facade.has_one_by_listing_id_for_date(
            listing_id=listing_financial_report_record.listing_id,
            target_date_str=str(listing_financial_report_record.created_at.date()),
        )
        assert result is True

    def has_one_by_listing_id_for_date_false(
        self, listing_financial_report_facade, mock_utcnow
    ):
        non_existent_id = "988d0b5d-d4a5-4808-a94d-2d9df1df7588"
        result = listing_financial_report_facade.has_one_by_listing_id_for_date(
            listing_id=non_existent_id,
            target_date_str=str(mock_utcnow.date()),
        )
        assert result is False

    def test_create_or_update_creates_new_record(
        self,
        listing_financial_report_facade,
        listing_record,
        expected_listing_financial_report_dict,
    ):
        result = listing_financial_report_facade.create_or_update(
            payload=expected_listing_financial_report_dict
        )

        assert self._compare_result_with_expected(
            result, expected_listing_financial_report_dict
        )

    def test_create_or_update_updates_existing_record(
        self,
        listing_financial_report_facade,
        listing_financial_report_record,
    ):
        listing_financial_report_entity = ListingFinancialReportEntity.model_validate(
            listing_financial_report_record
        )
        listing_financial_report_dict = listing_financial_report_entity.model_dump()
        updated_payload = {
            **listing_financial_report_dict,
            "ttm_occupancy_rate": (
                listing_financial_report_dict["ttm_occupancy_rate"] + 0.05
            ),
            "rating_overall": 4.95,
        }

        result = listing_financial_report_facade.create_or_update(
            payload=updated_payload
        )

        assert self._compare_result_with_expected(result, updated_payload)
        assert result.rating_overall != listing_financial_report_dict["rating_overall"]
