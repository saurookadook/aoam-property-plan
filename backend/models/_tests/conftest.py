from __future__ import annotations

from datetime import timedelta, timezone
from uuid import UUID

import pytest

from _factories.exchange_rate.db import ExchangeRateDBFactory
from _factories.market.db import MarketDBFactory
from _factories.market_financial_report.db import MarketFinancialReportDBFactory
from _factories.property.db import PropertyDBFactory


@pytest.fixture
def expected_market_dict():
    return dict(
        country="Test Country",
        district="Test District",
        locality="Test Locality",
        region="Test Region",
    )


@pytest.fixture
def test_market_record(expected_market_dict, test_db_session):
    market_record = MarketDBFactory(**expected_market_dict)
    test_db_session.commit()
    return market_record


@pytest.fixture
def expected_market_financial_report_dict(test_market_record):
    return dict(
        market_id=test_market_record.id,
        adr_cop=359677.0,
        adr_usd=100.0,
        annual_revenue_cop=35967700.0,
        annual_revenue_usd=1000.0,
        last_updated="2026-05-18T11:29:20.063778",
        listing_count=10.0,
        occupancy_rate=0.85,
        peak_months=["June", "July", "August"],
    )


@pytest.fixture
def test_market_financial_report_record(
    expected_market_financial_report_dict, test_db_session
):
    market_financial_report_record = MarketFinancialReportDBFactory(
        **expected_market_financial_report_dict
    )
    test_db_session.commit()
    return market_financial_report_record


@pytest.fixture
def expected_listing_dict(test_market_record):
    lng = -122.4194
    lat = 37.7749

    return dict(
        id=UUID("859d10d3-1fd0-4dd5-9b46-f10bd30f4fee"),
        adr_usd=150.0,
        airroi_id=UUID("e6b77c9d-5e83-4150-851b-81327f537dfd"),
        annual_revenue_usd=2000.0,
        bedrooms=3,
        latitude=lat,
        location=f"POINT({lng} {lat})",
        longitude=lng,
        market_id=test_market_record.id,
        occupancy_rate=0.75,
        property_type="Apartment",
        source_url="https://example.com/listing/12345",
    )


@pytest.fixture
def expected_property_dict(mock_utcnow):
    source_created_at = (
        (mock_utcnow - timedelta(days=30)).replace(tzinfo=timezone.utc).isoformat()
    )

    return dict(
        id=UUID("44cf56a4-1f14-4a08-915f-dc40b7ef657e"),
        address="123 Test St",
        bedrooms=3,
        city="Test City",
        country="Test Country",
        latitude=37.7749,
        longitude=-122.4194,
        neighborhood="Test Neighborhood",
        notes="Test notes",
        postal_code="12345",
        property_type="Apartment",
        purchase_price_cop=770000.0,
        purchase_price_usd=100000.0,
        source_created_at=source_created_at,
        source_url="https://example.com/property/12345",
        state="Test State",
    )


@pytest.fixture
def property_record(expected_property_dict, test_db_session):
    property_record = PropertyDBFactory(**expected_property_dict)
    test_db_session.commit()
    return property_record


@pytest.fixture
def expected_property_financial_report_dict(property_record, mock_utcnow):
    calculated_at = (
        (mock_utcnow - timedelta(days=5)).replace(tzinfo=timezone.utc).isoformat()
    )

    return dict(
        id=UUID("53cd9d19-65f7-4796-ac2c-b6616eb46d63"),
        property_id=property_record.id,
        annual_net_income_usd=50000.0,
        annual_revenue_usd=20000.0,
        calculated_at=calculated_at,
        cash_invested_usd=10000.0,
        coc_return_percentage=10.0,
        down_payment_percentage=20.0,
        exchange_rate=1.7,
        interest_rate=5.0,
        loan_term_years=30,
        monthly_expenses_usd=2000.0,
        payback_years=5.0,
    )


@pytest.fixture
def expected_exchange_rate_dict(mock_utcnow):
    record_date = (
        (mock_utcnow - timedelta(days=1))
        .replace(tzinfo=timezone.utc)
        .date()
        .isoformat()
    )

    return dict(
        id=UUID("5fd8ed45-5c16-47ab-b625-2cd37cc1f1a6"),
        record_date=record_date,
        cop_per_usd=500.0,
    )


@pytest.fixture
def exchange_rate_record(expected_exchange_rate_dict, test_db_session):
    exchange_rate = ExchangeRateDBFactory(**expected_exchange_rate_dict)
    test_db_session.commit()
    return exchange_rate
