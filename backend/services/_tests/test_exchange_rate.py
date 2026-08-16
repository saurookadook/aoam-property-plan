from __future__ import annotations

from datetime import timedelta

import pytest

from _factories.exchange_rate.db import ExchangeRateDBFactory
from models.exchange_rate.facade import ExchangeRateFacade
from services import exchange_rate as exchange_rate_service


@pytest.fixture
def frankfurter_url():
    return exchange_rate_service.FRANKFURTER_RATES_URL


class TestResolveCopPerUsd:
    def test_uses_the_stored_rate_without_calling_out(
        self, http_requests_mock, mock_utcnow, test_db_session
    ):
        """
        ``http_requests_mock`` runs with ``real_http=False``, so an unexpected
        outbound call would fail the test rather than hit the network.
        """
        target_date = mock_utcnow.date()
        ExchangeRateDBFactory(record_date=target_date, cop_per_usd=4150.0)
        test_db_session.commit()

        result = exchange_rate_service.resolve_cop_per_usd(
            test_db_session, on_date=target_date
        )

        assert result is not None
        assert result.cop_per_usd == 4150.0
        assert http_requests_mock.call_count == 0

    def test_falls_back_to_the_most_recent_earlier_rate(
        self, http_requests_mock, mock_utcnow, test_db_session
    ):
        target_date = mock_utcnow.date()
        ExchangeRateDBFactory(
            record_date=target_date - timedelta(days=4), cop_per_usd=4100.0
        )
        test_db_session.commit()

        result = exchange_rate_service.resolve_cop_per_usd(
            test_db_session, on_date=target_date
        )

        assert result is not None
        assert result.cop_per_usd == 4100.0
        assert http_requests_mock.call_count == 0

    def test_fetches_and_stores_a_rate_on_a_cold_database(
        self, http_requests_mock, frankfurter_url, mock_utcnow, test_db_session
    ):
        """
        ``handle_exchange_rate`` only writes a rate row for a date that already has
        a listing financial report, so a fresh environment can hold no rates at
        all. The first property added must still get a USD price.
        """
        target_date = mock_utcnow.date()
        http_requests_mock.get(
            frankfurter_url,
            json=[
                {
                    "base": "USD",
                    "quote": "COP",
                    "date": str(target_date),
                    "rate": 4150.0,
                }
            ],
        )

        result = exchange_rate_service.resolve_cop_per_usd(
            test_db_session, on_date=target_date
        )

        assert result is not None
        assert result.cop_per_usd == 4150.0
        assert http_requests_mock.call_count == 1

        # ...and it was persisted, so the next call needs no network
        stored = ExchangeRateFacade(db_session=test_db_session).get_latest_on_or_before(
            target_date
        )
        assert stored is not None
        assert stored.cop_per_usd == 4150.0

    def test_returns_none_when_the_rate_api_fails(
        self, http_requests_mock, frankfurter_url, mock_utcnow, test_db_session
    ):
        http_requests_mock.get(frankfurter_url, status_code=503)

        result = exchange_rate_service.resolve_cop_per_usd(
            test_db_session, on_date=mock_utcnow.date()
        )

        assert result is None

    def test_returns_none_when_the_rate_api_returns_nothing_usable(
        self, http_requests_mock, frankfurter_url, mock_utcnow, test_db_session
    ):
        http_requests_mock.get(frankfurter_url, json=[])

        result = exchange_rate_service.resolve_cop_per_usd(
            test_db_session, on_date=mock_utcnow.date()
        )

        assert result is None


class TestConvertCopToUsd:
    def test_converts_using_the_given_rate(self):
        assert exchange_rate_service.convert_cop_to_usd(
            700000000, 4150.0
        ) == pytest.approx(168674.698, rel=1e-5)

    @pytest.mark.parametrize(
        "amount_cop, cop_per_usd",
        [
            (None, 4150.0),
            (700000000, None),
            (700000000, 0),
        ],
    )
    def test_returns_none_for_unusable_input(self, amount_cop, cop_per_usd):
        assert exchange_rate_service.convert_cop_to_usd(amount_cop, cop_per_usd) is None
