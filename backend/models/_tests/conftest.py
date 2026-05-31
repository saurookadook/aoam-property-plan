from __future__ import annotations

from uuid import UUID

import pytest


@pytest.fixture
def expected_market_dict():
    return dict(
        id=UUID("44cf56a4-1f14-4a08-915f-dc40b7ef657e"),
        adr_usd=100.0,
        annual_revenue_usd=1000.0,
        city="Test City",
        country="Test Country",
        listing_count=10,
        last_updated="2026-05-18T11:29:20.063778",
        neighborhood="Test Neighborhood",
        occupancy_rate=0.85,
        peak_months=["June", "July", "August"],
    )
