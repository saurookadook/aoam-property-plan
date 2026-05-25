from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

import factory
import pytest
from sqlalchemy import select, and_

from _factories.market.db import MarketDBFactory
from models.market.db import MarketDB


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


def test_market_db(expected_market_dict, mock_utcnow, test_db_session):
    market = MarketDBFactory(**expected_market_dict)
    test_db_session.commit()

    result = test_db_session.execute(
        select(MarketDB).where(
            and_(
                MarketDB.id == expected_market_dict["id"],
                MarketDB.city == expected_market_dict["city"],
            )
        )
    ).scalar_one()

    assert result.id == expected_market_dict["id"]
    assert result.adr_usd == expected_market_dict["adr_usd"]
    assert result.annual_revenue_usd == expected_market_dict["annual_revenue_usd"]
    assert result.city == expected_market_dict["city"]
    assert result.country == expected_market_dict["country"]
    assert result.listing_count == expected_market_dict["listing_count"]
    assert result.neighborhood == expected_market_dict["neighborhood"]
    assert result.occupancy_rate == expected_market_dict["occupancy_rate"]
    assert result.peak_months == expected_market_dict["peak_months"]
    assert result.last_updated.isoformat() == expected_market_dict["last_updated"]
    assert isinstance(result.created_at, datetime)
    assert isinstance(result.updated_at, datetime)
    assert (
        result.created_at.replace(tzinfo=timezone.utc).isoformat()
        == mock_utcnow.isoformat()
    )
    assert (
        result.updated_at.replace(tzinfo=timezone.utc).isoformat()
        == mock_utcnow.isoformat()
    )
