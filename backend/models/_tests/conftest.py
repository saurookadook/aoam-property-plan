from __future__ import annotations

from datetime import timedelta, timezone
from uuid import UUID

import pytest

from _factories.exchange_rate.db import ExchangeRateDBFactory
from _factories.listing.db import ListingDBFactory
from _factories.market.db import MarketDBFactory
from _factories.market_financial_report.db import MarketFinancialReportDBFactory
from _factories.property.db import PropertyDBFactory
from _factories.property_comp.db import PropertyCompDBFactory


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
        monthly_revenue_distribution=[
            0.07,
            0.06,
            0.08,
            0.09,
            0.08,
            0.11,
            0.12,
            0.11,
            0.07,
            0.07,
            0.06,
            0.08,
        ],
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
        airroi_id=2341532,
        amenities=["Wifi", "Pool", "Kitchen"],
        baths=2.5,
        beds=3,
        bedrooms=3,
        cover_photo_url="https://example.com/listing/12345/cover.jpg",
        description="A lovely test listing.",
        latitude=lat,
        location=f"POINT({lng} {lat})",
        longitude=lng,
        market_id=test_market_record.id,
        name="Test Listing",
        photo_urls=[
            "https://example.com/listing/12345/photo1.jpg",
            "https://example.com/listing/12345/photo2.jpg",
        ],
        property_type="Apartment",
        source_url="https://example.com/listing/12345",
    )


@pytest.fixture
def listing_record(expected_listing_dict, test_db_session):
    listing = ListingDBFactory(**expected_listing_dict)
    test_db_session.commit()
    return listing


@pytest.fixture
def expected_listing_financial_report_dict(expected_listing_dict):
    return dict(
        id=UUID("859d10d3-1fd0-4dd5-9b46-f10bd30f4fee"),
        listing_id=expected_listing_dict["id"],
        # adr_cop=539515.5,
        # adr_usd=150.0,
        # annual_revenue_cop=7193540.0,
        # annual_revenue_usd=2000.0,
        # occupancy_rate=0.75,
    )


@pytest.fixture
def expected_property_dict(mock_utcnow, test_market_record):
    source_created_at = (
        (mock_utcnow - timedelta(days=30)).replace(tzinfo=timezone.utc).isoformat()
    )

    return dict(
        id=UUID("44cf56a4-1f14-4a08-915f-dc40b7ef657e"),
        address="123 Test St",
        amenities=["Patio", "Servicios Públicos"],
        baths=2.5,
        bedrooms=3,
        city="Test City",
        country="Test Country",
        description="A lovely test property.",
        guests=6,
        latitude=37.7749,
        longitude=-122.4194,
        market_id=test_market_record.id,
        name="Test Property",
        neighborhood="Test Neighborhood",
        notes="Test notes",
        postal_code="12345",
        property_type="Apartment",
        purchase_price_cop=770000.0,
        purchase_price_usd=100000.0,
        source_created_at=source_created_at,
        source_url="https://example.com/property/12345",
        state="Test State",
        status="active",
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
        annual_net_income_cop=17983850.0,
        annual_net_income_usd=5000.0,
        annual_revenue_cop=7193540.0,
        annual_revenue_usd=2000.0,
        calculated_at=calculated_at,
        cash_invested_usd=10000.0,
        coc_return_percentage=10.0,
        down_payment_percentage=20.0,
        exchange_rate=1.7,
        interest_rate=5.0,
        loan_term_years=30,
        monthly_expenses_cop=359677.0,
        monthly_expenses_usd=100.0,
        payback_years=5.0,
    )


@pytest.fixture
def expected_property_comp_dict(listing_record, mock_utcnow, property_record):
    captured_at = mock_utcnow.replace(tzinfo=timezone.utc).isoformat()

    return dict(
        id=UUID("0c9ef0a2-3d4f-4b21-9c5e-7a1f2b8d4e63"),
        property_id=property_record.id,
        listing_id=listing_record.id,
        adr_cop=349873.7,
        captured_at=captured_at,
        distance_km=0.42,
        occupancy_rate=0.423,
        ttm_revenue_cop=52217691.0,
        ttm_total_days=365.0,
    )


@pytest.fixture
def property_comp_record(expected_property_comp_dict, test_db_session):
    property_comp = PropertyCompDBFactory(**expected_property_comp_dict)
    test_db_session.commit()
    return property_comp


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
