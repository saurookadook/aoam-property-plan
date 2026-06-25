from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any, Callable, Generator

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from _factories.listing.db import ListingDBFactory
from _factories.listing.entity import ListingEntityFactory
from _factories.listing_financial_report.db import ListingFinancialReportDBFactory
from _factories.market.db import MarketDBFactory
from api.crons.handlers import handle_exchange_rate
from models.exchange_rate.db import ExchangeRateDB
from models.exchange_rate.facade import ExchangeRateFacade

if TYPE_CHECKING:
    from models.listing.db import ListingDB
    from models.market.db import MarketDB


@pytest.fixture
def mock_frankfurter_api_response(mock_utcnow):
    base_rate_entry = {
        "base": "USD",
        "quote": "COP",
    }

    return [
        {
            **base_rate_entry,
            "date": str(mock_utcnow.date()),
            "rate": 3502.24,
        },
        {
            **base_rate_entry,
            "date": str((mock_utcnow + timedelta(days=2)).date()),
            "rate": 3482.84,
        },
        {
            **base_rate_entry,
            "date": str((mock_utcnow + timedelta(days=3)).date()),
            "rate": 3457.79,
        },
        {
            **base_rate_entry,
            "date": str((mock_utcnow + timedelta(days=4)).date()),
            "rate": 3436.24,
        },
        {
            **base_rate_entry,
            "date": str((mock_utcnow + timedelta(days=5)).date()),
            "rate": 3456.42,
        },
        {
            **base_rate_entry,
            "date": str((mock_utcnow + timedelta(days=6)).date()),
            "rate": 3458.18,
        },
        {
            **base_rate_entry,
            "date": str((mock_utcnow + timedelta(days=8)).date()),
            "rate": 3451.46,
        },
        {
            **base_rate_entry,
            "date": str((mock_utcnow + timedelta(days=9)).date()),
            "rate": 3434.87,
        },
        {
            **base_rate_entry,
            "date": str((mock_utcnow + timedelta(days=10)).date()),
            "rate": 3426.3,
        },
    ]


@pytest.fixture
def frankfurter_resp_callback(
    mock_frankfurter_api_response, mock_utcnow: datetime
) -> Callable[..., list[dict]]:
    def _matcher(request, context):
        if not request.qs.get("from", None) and not request.qs.get("to", None):
            maybe_record = next(
                (
                    record
                    for record in mock_frankfurter_api_response
                    if record["date"] == str(mock_utcnow.date())
                ),
                None,
            )
            if maybe_record:
                context.status_code = 200
                return [maybe_record]
            context.status_code = 404
            return []

        start_index = 0
        end_index = len(mock_frankfurter_api_response)

        if request.qs["from"]:
            start_index = next(
                (
                    i
                    for i, record in enumerate(mock_frankfurter_api_response)
                    if record["date"] == request.qs["from"][0]
                ),
                start_index,
            )
        if request.qs["to"]:
            end_index = next(
                (
                    i + 1
                    for i, record in enumerate(mock_frankfurter_api_response)
                    if record["date"] == request.qs["to"][0]
                ),
                end_index,
            )

        context.status_code = 200
        return mock_frankfurter_api_response[start_index:end_index]

    return _matcher


@pytest.fixture
def frankfurter_request_mocks(
    frankfurter_resp_callback: Callable[..., list[dict]],
    http_requests_mock,
) -> Generator[Any, Any, None]:
    http_requests_mock.get(
        "https://api.frankfurter.dev/v2/rates",
        json=frankfurter_resp_callback,
    )
    yield http_requests_mock


class TestHandleExchangeRate:

    @pytest.fixture
    def exchange_rate_facade(self, test_db_session: Session) -> ExchangeRateFacade:
        return ExchangeRateFacade(db_session=test_db_session)

    @pytest.fixture
    def mock_market(self, test_db_session: Session) -> MarketDB:
        market = MarketDBFactory()
        test_db_session.commit()
        return market

    @pytest.fixture
    def mock_listing(
        self,
        mock_market: MarketDB,
        mock_utcnow: datetime,
        test_db_session: Session,
    ) -> ListingDB:
        listing = ListingDBFactory(
            **ListingEntityFactory(
                market_id=mock_market.id,
                created_at=mock_utcnow,
                updated_at=mock_utcnow + timedelta(seconds=2),
            ).model_dump(),
        )
        test_db_session.commit()
        return listing

    def test_creates_new_exchange_rate_record(
        self,
        frankfurter_request_mocks: Generator[Any, Any, None],
        mock_frankfurter_api_response: list[dict],
        mock_listing: ListingDB,
        mock_utcnow: datetime,
        test_db_session: Session,
    ):
        ListingFinancialReportDBFactory(
            listing_id=mock_listing.id,
            created_at=mock_utcnow + timedelta(seconds=5),
            updated_at=mock_utcnow + timedelta(seconds=7),
        )
        test_db_session.commit()

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

    def test_does_not_create_new_exchange_rate_record_without_listing_financial_report(
        self,
        frankfurter_request_mocks: Generator[Any, Any, None],
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

        assert len(exchange_rate_records_after) == 0

    def test_handles_start_and_end_dates(
        self,
        frankfurter_request_mocks: Generator[Any, Any, None],
        mock_frankfurter_api_response: list[dict],
        mock_listing: ListingDB,
        mock_utcnow: datetime,
        test_db_session: Session,
    ):
        lfr_dates = [
            mock_utcnow.date(),
            (mock_utcnow + timedelta(days=2)).date(),
            (mock_utcnow + timedelta(days=3)).date(),
            (mock_utcnow + timedelta(days=6)).date(),
        ]

        for date in lfr_dates:
            ListingFinancialReportDBFactory(
                listing_id=mock_listing.id,
                created_at=datetime.fromisoformat(str(date)),
                updated_at=datetime.fromisoformat(str(date)) + timedelta(seconds=2),
            )
        test_db_session.commit()

        exchange_rate_records_before = (
            test_db_session.execute(select(ExchangeRateDB)).scalars().all()
        )
        assert len(exchange_rate_records_before) == 0

        handle_exchange_rate(
            start_date=str(mock_utcnow.date()),
            end_date=str((mock_utcnow + timedelta(days=6)).date()),
        )

        exchange_rate_records_after = (
            test_db_session.execute(select(ExchangeRateDB)).scalars().all()
        )

        assert len(exchange_rate_records_after) == len(lfr_dates)

        for exchange_rate, lfr_date in zip(exchange_rate_records_after, lfr_dates):
            assert str(exchange_rate.record_date) == str(lfr_date)
            assert exchange_rate.cop_per_usd == next(
                (
                    item["rate"]
                    for item in mock_frankfurter_api_response
                    if item["date"] == str(lfr_date)
                ),
                None,
            )
