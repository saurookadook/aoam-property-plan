from __future__ import annotations

from typing import Any, Callable, Generator

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from api.crons.handlers import handle_exchange_rate
from models.exchange_rate.db import ExchangeRateDB
from models.exchange_rate.facade import ExchangeRateFacade


@pytest.fixture
def mock_frankfurter_api_response(mock_utcnow):
    return [
        {
            "date": str(mock_utcnow.date()),
            "base": "USD",
            "quote": "COP",
            "rate": 3428.3,
        }
    ]


@pytest.fixture
def frankfurter_resp_callback(
    mock_frankfurter_api_response,
) -> Callable[..., list[dict]]:
    def _matcher(request, context):
        context.status_code = 200
        return mock_frankfurter_api_response

    return _matcher


@pytest.fixture
def frankfurter_request_mocks(
    frankfurter_resp_callback: Callable[..., list[dict]],
    http_requests_mock,
) -> Generator[Any, Any, None]:
    http_requests_mock.get(
        "https://api.frankfurter.dev/v2/rates?base=USD&quotes=COP",
        json=frankfurter_resp_callback,
    )
    yield http_requests_mock


class TestHandleExchangeRate:

    @pytest.fixture
    def exchange_rate_facade(self, test_db_session: Session) -> ExchangeRateFacade:
        return ExchangeRateFacade(db_session=test_db_session)

    def test_creates_new_exchange_rate_record(
        self,
        frankfurter_request_mocks: Generator[Any, Any, None],
        mock_frankfurter_api_response: list[dict],
        test_db_session: Session,
    ):
        exchange_rate_records_before = (
            test_db_session.execute(select(ExchangeRateDB)).scalars().all()
        )
        assert len(exchange_rate_records_before) == 0

        handle_exchange_rate()

        exchange_rate_records_after = (
            test_db_session.execute(select(ExchangeRateDB)).scalars().all()
        )

        assert len(exchange_rate_records_after) > 0
        assert (
            str(exchange_rate_records_after[0].record_date)
            == mock_frankfurter_api_response[0]["date"]
        )
        assert (
            exchange_rate_records_after[0].cop_per_usd
            == mock_frankfurter_api_response[0]["rate"]
        )
