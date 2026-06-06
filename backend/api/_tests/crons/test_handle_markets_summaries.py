from __future__ import annotations

import json
from typing import Any, Callable, Generator

import pytest
from sqlalchemy import select

from _factories.market.db import MarketDBFactory
from api.crons.handlers import handle_markets_summaries
from models.market.db import MarketDB
from models.market.facade import MarketFacade
from models.market_financial_report.db import MarketFinancialReportDB
from utils.filesystem import get_module_root


@pytest.fixture
def market_summary_seed_files() -> list[dict]:
    seeds_path = get_module_root(__file__) / "scripts" / "db" / "seeding" / "seed_data"
    seed_files = []
    for seed_file in seeds_path.glob("*.json"):
        with open(seed_file, "r") as f:
            data = json.load(f)
            seed_files.append(data)
    return seed_files


@pytest.fixture
def markets_data_from_seeds(market_summary_seed_files) -> list[dict]:
    return [seed_file["market"] for seed_file in market_summary_seed_files]


@pytest.fixture
def dynamic_resp_callback(market_summary_seed_files) -> Callable[..., dict]:
    def _matcher(request, context):
        request_body = json.loads(request.body)
        for seed_file in market_summary_seed_files:
            if (
                seed_file["market"]["country"] == request_body["market"]["country"]
                and seed_file["market"]["region"] == request_body["market"]["region"]
                and seed_file["market"]["locality"]
                == request_body["market"]["locality"]
            ):
                context.status_code = 200
                return seed_file
        context.status_code = 404
        return {}

    return _matcher


@pytest.fixture
def airroi_request_mocks(
    dynamic_resp_callback, http_requests_mock
) -> Generator[Any, Any, None]:
    http_requests_mock.post(
        "https://api.airroi.com/markets/summary", json=dynamic_resp_callback
    )
    yield http_requests_mock


class TestHandleMarketsSummaries:

    @pytest.fixture
    def market_facade(self, test_db_session):
        return MarketFacade(db_session=test_db_session)

    @pytest.fixture
    def market_records(self, markets_data_from_seeds, test_db_session):
        markets = [
            MarketDBFactory(**market_dict) for market_dict in markets_data_from_seeds
        ]
        test_db_session.commit()
        return markets

    def test_creates_new_market_and_market_financial_report_records(
        self,
        airroi_request_mocks,
        market_records,
        market_summary_seed_files,
        test_db_session,
    ):
        market_financial_report_records_before = (
            test_db_session.execute(select(MarketFinancialReportDB)).scalars().all()
        )
        assert len(market_financial_report_records_before) == 0

        handle_markets_summaries()

        market_financial_report_records_after = (
            test_db_session.execute(select(MarketFinancialReportDB)).scalars().all()
        )

        assert len(market_financial_report_records_after) == len(
            market_summary_seed_files
        )
        for mfr in market_financial_report_records_after:
            market_record = test_db_session.execute(
                select(MarketDB).where(MarketDB.id == mfr.market_id)
            ).scalar_one()

            seed_data = next(
                (
                    seed
                    for seed in market_summary_seed_files
                    if seed["market"]["country"] == market_record.country
                    and seed["market"]["region"] == market_record.region
                    and seed["market"]["locality"] == market_record.locality
                ),
                None,
            )

            assert market_record is not None
            assert seed_data is not None
            assert market_record.country == seed_data["market"]["country"]
            assert market_record.region == seed_data["market"]["region"]
            assert market_record.locality == seed_data["market"]["locality"]
            assert mfr.adr_usd == seed_data["average_daily_rate"]
            assert mfr.annual_revenue_usd == seed_data["revenue"]
            assert mfr.listing_count == seed_data["active_listings_count"]
            assert mfr.occupancy_rate == seed_data["occupancy"]
            assert mfr.peak_months == seed_data.get("peak_months", None)
