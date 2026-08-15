from __future__ import annotations

from datetime import date, timedelta

import pytest

from _factories.exchange_rate.db import ExchangeRateDBFactory
from models.exchange_rate.entity import ExchangeRateEntity
from models.exchange_rate.facade import ExchangeRateFacade


class TestExchangeRateFacade:
    @pytest.fixture
    def exchange_rate_facade(self, test_db_session):
        return ExchangeRateFacade(db_session=test_db_session)

    def _compare_result_with_expected(
        self, result: ExchangeRateEntity, expected_dict: dict
    ):
        for key, value in expected_dict.items():
            if key == "record_date" and isinstance(value, str):
                assert result.record_date.isoformat() == value
            elif key == "record_date" and isinstance(value, date):
                assert result.record_date == value
            else:
                assert getattr(result, key) == value

        return True

    def test_get_one_by_id(self, exchange_rate_facade, exchange_rate_record):
        result = exchange_rate_facade.get_one_by_id(exchange_rate_record.id)
        assert result == ExchangeRateEntity.model_validate(exchange_rate_record)

    def test_get_one_by_id_no_result(self, exchange_rate_facade):
        with pytest.raises(ExchangeRateFacade.NoResultFound):
            non_existent_id = "988d0b5d-d4a5-4808-a94d-2d9df1df7588"
            exchange_rate_facade.get_one_by_id(non_existent_id)

    def test_get_one_by_date(self, exchange_rate_facade, exchange_rate_record):
        result = exchange_rate_facade.get_one_by_date(exchange_rate_record.record_date)
        assert result == ExchangeRateEntity.model_validate(exchange_rate_record)

    def test_get_one_by_date_no_result(self, exchange_rate_facade):
        with pytest.raises(ExchangeRateFacade.NoResultFound):
            non_existent_date = "2024-01-01"
            exchange_rate_facade.get_one_by_date(non_existent_date)

    def test_get_latest_on_or_before_returns_exact_match(
        self, exchange_rate_facade, exchange_rate_record
    ):
        result = exchange_rate_facade.get_latest_on_or_before(
            exchange_rate_record.record_date
        )
        assert result == ExchangeRateEntity.model_validate(exchange_rate_record)

    def test_get_latest_on_or_before_returns_most_recent_earlier_record(
        self, exchange_rate_facade, mock_utcnow, test_db_session
    ):
        target_date = mock_utcnow.date()
        ExchangeRateDBFactory(
            record_date=target_date - timedelta(days=10), cop_per_usd=4000.0
        )
        most_recent = ExchangeRateDBFactory(
            record_date=target_date - timedelta(days=3), cop_per_usd=4150.0
        )
        test_db_session.commit()

        result = exchange_rate_facade.get_latest_on_or_before(target_date)

        assert result is not None
        assert result.record_date == most_recent.record_date
        assert result.cop_per_usd == 4150.0

    def test_get_latest_on_or_before_ignores_later_records(
        self, exchange_rate_facade, mock_utcnow, test_db_session
    ):
        target_date = mock_utcnow.date()
        earlier = ExchangeRateDBFactory(
            record_date=target_date - timedelta(days=2), cop_per_usd=4100.0
        )
        ExchangeRateDBFactory(
            record_date=target_date + timedelta(days=2), cop_per_usd=4300.0
        )
        test_db_session.commit()

        result = exchange_rate_facade.get_latest_on_or_before(target_date)

        assert result is not None
        assert result.record_date == earlier.record_date
        assert result.cop_per_usd == 4100.0

    def test_get_latest_on_or_before_returns_none_when_no_records(
        self, exchange_rate_facade, mock_utcnow
    ):
        """
        The cold-start case: ``handle_exchange_rate`` only writes a row when a
        listing financial report exists for that date, so a fresh database can
        legitimately have no rates at all. This must return ``None``, not raise.
        """
        result = exchange_rate_facade.get_latest_on_or_before(mock_utcnow.date())

        assert result is None

    def test_get_latest_on_or_before_returns_none_when_all_records_are_later(
        self, exchange_rate_facade, mock_utcnow, test_db_session
    ):
        target_date = mock_utcnow.date()
        ExchangeRateDBFactory(
            record_date=target_date + timedelta(days=1), cop_per_usd=4200.0
        )
        test_db_session.commit()

        result = exchange_rate_facade.get_latest_on_or_before(target_date)

        assert result is None

    def test_create_or_update_creates_new_record(
        self, exchange_rate_facade, expected_exchange_rate_dict
    ):
        result = exchange_rate_facade.create_or_update(
            payload=expected_exchange_rate_dict
        )

        assert self._compare_result_with_expected(result, expected_exchange_rate_dict)

    def test_create_or_update_updates_existing_record(
        self, exchange_rate_facade, exchange_rate_record
    ):
        exchange_rate_entity = ExchangeRateEntity.model_validate(exchange_rate_record)
        exchange_rate_record_dict = exchange_rate_entity.model_dump()
        updated_payload = {
            **exchange_rate_record_dict,
            "cop_per_usd": exchange_rate_record_dict["cop_per_usd"] + 10,
        }

        result = exchange_rate_facade.create_or_update(payload=updated_payload)

        assert self._compare_result_with_expected(result, updated_payload)
        assert result.cop_per_usd != exchange_rate_record_dict["cop_per_usd"]
