from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from _factories.market_financial_report.db import (
    MarketFinancialReportDBFactory,
)
from models.market_financial_report.entity import MarketFinancialReportEntity
from models.market_financial_report.facade import MarketFinancialReportFacade


class TestMarketFinancialReportFacade:
    @pytest.fixture
    def market_financial_report_facade(self, test_db_session):
        return MarketFinancialReportFacade(db_session=test_db_session)

    @pytest.fixture
    def market_financial_report_record(
        self, expected_market_financial_report_dict, test_db_session
    ):
        market_financial_report = MarketFinancialReportDBFactory(
            **expected_market_financial_report_dict
        )
        test_db_session.commit()
        return market_financial_report

    def _compare_result_with_expected(
        self,
        result: MarketFinancialReportEntity,
        expected_dict: dict,
    ):
        for key, value in expected_dict.items():
            if key == "last_updated":
                expected_dt = datetime.fromisoformat(value).replace(tzinfo=None)
                assert result.last_updated == expected_dt
            else:
                assert getattr(result, key) == value

        return True

    def test_get_one_by_id(
        self,
        market_financial_report_facade,
        market_financial_report_record,
    ):
        result = market_financial_report_facade.get_one_by_id(
            market_financial_report_record.id
        )
        assert result == MarketFinancialReportEntity.model_validate(
            market_financial_report_record
        )

    def test_get_one_by_id_no_result(self, market_financial_report_facade):
        with pytest.raises(MarketFinancialReportFacade.NoResultFound):
            non_existent_id = "988d0b5d-d4a5-4808-a94d-2d9df1df7588"
            market_financial_report_facade.get_one_by_id(non_existent_id)

    def test_create_or_update_creates_new_record(
        self,
        market_financial_report_facade,
        expected_market_financial_report_dict,
    ):
        result = market_financial_report_facade.create_or_update(
            payload=expected_market_financial_report_dict
        )

        assert self._compare_result_with_expected(
            result, expected_market_financial_report_dict
        )

    def test_create_or_update_updates_existing_record(
        self,
        market_financial_report_facade,
        market_financial_report_record,
    ):
        market_financial_report_entity = MarketFinancialReportEntity.model_validate(
            market_financial_report_record
        )
        market_financial_report_dict = market_financial_report_entity.model_dump()
        updated_payload = {
            **market_financial_report_dict,
            "last_updated": (
                market_financial_report_entity.last_updated + timedelta(days=1)
            ).isoformat(),
            "occupancy_rate": (market_financial_report_dict["occupancy_rate"] + 0.05),
        }

        result = market_financial_report_facade.create_or_update(
            payload=updated_payload
        )

        assert self._compare_result_with_expected(result, updated_payload)
        assert result.last_updated > market_financial_report_dict["last_updated"]
        assert result.occupancy_rate != market_financial_report_dict["occupancy_rate"]
