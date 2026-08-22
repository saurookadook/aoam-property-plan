from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

import pytest
from fastapi import status

from _factories.exchange_rate.db import ExchangeRateDBFactory


class TestReadExchangeRateRoute:
    def test_returns_the_stored_rate(self, test_app_client, test_db_session):
        ExchangeRateDBFactory(record_date=date(2026, 4, 19), cop_per_usd=4100.5)
        test_db_session.commit()

        result = test_app_client.get("/api/exchange-rate")

        assert result.status_code == 200
        assert result.json() == {
            "data": {"cop_per_usd": 4100.5, "record_date": "2026-04-19"}
        }

    def test_returns_the_most_recent_rate(self, test_app_client, test_db_session):
        ExchangeRateDBFactory(record_date=date(2026, 4, 1), cop_per_usd=3900.0)
        ExchangeRateDBFactory(record_date=date(2026, 4, 19), cop_per_usd=4100.5)
        test_db_session.commit()

        result = test_app_client.get("/api/exchange-rate")

        assert result.status_code == 200
        assert result.json()["data"]["cop_per_usd"] == 4100.5

    def test_ignores_a_rate_recorded_in_the_future(
        self, test_app_client, test_db_session
    ):
        """
        ``resolve_cop_per_usd`` asks for the latest rate on or before today, so a
        row dated ahead of today is not "the current rate" - it is a row that
        should not have been written.

        Anchored on the real current date rather than ``mock_utcnow``: the
        service binds ``datetime`` at import, so the ``patch_utcnow`` fixture
        does not reach it, and a fixed "future" date would quietly become a past
        one as the calendar moved past it.
        """
        today = datetime.now(timezone.utc).date()

        ExchangeRateDBFactory(
            record_date=today + timedelta(days=30), cop_per_usd=9999.0
        )
        ExchangeRateDBFactory(record_date=today - timedelta(days=1), cop_per_usd=4100.5)
        test_db_session.commit()

        result = test_app_client.get("/api/exchange-rate")

        assert result.status_code == 200
        assert result.json()["data"]["cop_per_usd"] == 4100.5

    def test_serves_503_when_no_rate_can_be_resolved(
        self, test_app_client, mocker, test_db_session
    ):
        """
        A 503 rather than a 200 carrying a null: a currency toggle with nothing
        to convert by is a broken feature, not an empty result.
        """
        mocker.patch(
            "api.routes.exchange_rate.resolve_cop_per_usd",
            return_value=None,
        )

        result = test_app_client.get("/api/exchange-rate")

        assert result.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert result.json() == {"detail": "No exchange rate available"}

    def test_serves_500_when_resolving_raises(
        self, test_app_client, mocker, test_db_session
    ):
        mocker.patch(
            "api.routes.exchange_rate.resolve_cop_per_usd",
            side_effect=RuntimeError("frankfurter is on fire"),
        )

        result = test_app_client.get("/api/exchange-rate")

        assert result.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert result.json() == {"detail": "Error fetching exchange rate"}

    @pytest.mark.parametrize("excluded_key", ["id", "created_at", "updated_at"])
    def test_serves_only_the_rate_and_its_date(
        self, excluded_key, test_app_client, test_db_session
    ):
        """
        The response is deliberately narrower than ``ExchangeRateEntity`` - the
        client needs the number and the day it was true, and nothing else.
        """
        ExchangeRateDBFactory(record_date=date(2026, 4, 19), cop_per_usd=4100.5)
        test_db_session.commit()

        result = test_app_client.get("/api/exchange-rate")

        assert excluded_key not in result.json()["data"]
