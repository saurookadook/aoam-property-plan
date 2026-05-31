from __future__ import annotations

from uuid import UUID

import pytest

from _factories.market.db import MarketDBFactory


@pytest.fixture
def expected_market_dict():
    return dict(
        adr_usd=100.0,
        annual_revenue_usd=1000.0,
        city="Test City",
        country="Test Country",
        last_updated="2026-05-18T11:29:20.063778",
        listing_count=10.0,
        neighborhood="Test Neighborhood",
        occupancy_rate=0.85,
        peak_months=["June", "July", "August"],
        region="Test Region",
    )


@pytest.fixture
def test_market_record(expected_market_dict, test_db_session):
    market_record = MarketDBFactory(**expected_market_dict)
    test_db_session.commit()
    return market_record


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
