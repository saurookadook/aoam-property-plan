from __future__ import annotations

from datetime import datetime, timedelta

import pytest
from sqlalchemy.orm import Session

from _factories.market.db import MarketDBFactory
from _factories.market.entity import MarketEntity, MarketEntityFactory
from _factories.market_financial_report.db import (
    MarketFinancialReportDBFactory,
)
from _factories.market_financial_report.entity import MarketFinancialReportEntityFactory
from models.market.facade import MarketFacade
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

    @pytest.fixture
    def create_market_and_financial_records(self):
        def _factory(
            db_session: Session, *, number_of_reports: int = 3
        ) -> tuple[MarketEntity, list[MarketFinancialReportEntity]]:
            market = MarketEntityFactory()
            MarketDBFactory(**market.model_dump())
            db_session.commit()

            reports = []

            for _ in range(number_of_reports):
                mfr = MarketFinancialReportEntityFactory(market_id=market.id)
                MarketFinancialReportDBFactory(**mfr.model_dump())
                reports.append(mfr)
            db_session.commit()

            return market, reports

        return _factory

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

    def test_get_all_by_market_id(
        self,
        create_market_and_financial_records,
        market_financial_report_facade,
        test_db_session,
    ):
        other_market, other_mfrs = create_market_and_financial_records(
            test_db_session, number_of_reports=5
        )
        expected_market, expected_mfrs = create_market_and_financial_records(
            test_db_session
        )

        results = market_financial_report_facade.get_all_by_market_id(
            expected_market.id
        )

        assert len(results) != len(other_mfrs)
        assert len(results) == len(expected_mfrs)

        for mfr in results:
            assert mfr.market_id != other_market.id
            assert mfr.market_id == expected_market.id

    def test_get_all_by_market_id_no_result(
        self, market_financial_report_facade, test_db_session
    ):
        market = MarketDBFactory()
        test_db_session.commit()

        results = market_financial_report_facade.get_all_by_market_id(market.id)

        assert results == []

    def test_get_all_by_market_id_no_market(self, market_financial_report_facade):
        non_existent_market_id = "855ff18a-088d-41fe-bcd2-35ecbeae0793"

        with pytest.raises(MarketFacade.NoResultFound):
            market_financial_report_facade.get_all_by_market_id(non_existent_market_id)

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

    def test_get_latest_by_market_id_returns_none_when_never_summarised(
        self, market_financial_report_facade, test_market_record
    ):
        assert (
            market_financial_report_facade.get_latest_by_market_id(
                test_market_record.id
            )
            is None
        )

    def test_get_latest_by_market_id(
        self,
        market_financial_report_facade,
        mock_utcnow,
        test_market_record,
        test_db_session,
    ):
        # ``handle_markets_summaries`` inserts a fresh row per run rather than
        # updating one, so "the report" for a market has to mean the latest of
        # a history.
        older = MarketFinancialReportDBFactory(
            market_id=test_market_record.id,
            last_updated=mock_utcnow - timedelta(days=7),
        )
        newest = MarketFinancialReportDBFactory(
            market_id=test_market_record.id,
            last_updated=mock_utcnow - timedelta(days=1),
        )
        test_db_session.commit()

        result = market_financial_report_facade.get_latest_by_market_id(
            test_market_record.id
        )

        assert result is not None
        assert result.id == newest.id
        assert result.id != older.id
