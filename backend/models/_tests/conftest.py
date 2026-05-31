from __future__ import annotations

import pytest


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
