from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

import pytest
from geoalchemy2.elements import WKBElement, WKTElement
from geoalchemy2.functions import ST_GeogFromWKB
from sqlalchemy import select, and_

from _factories.listing.db import ListingDBFactory
from _factories.market.db import MarketDBFactory
from models.listing.db import ListingDB
from models.market.db import MarketDB


@pytest.fixture
def test_market_record(test_db_session):
    market_record = MarketDBFactory(
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


def test_listing_db(expected_listing_dict, mock_utcnow, test_db_session):
    listing = ListingDBFactory(**expected_listing_dict)
    test_db_session.commit()

    result = test_db_session.execute(
        select(ListingDB).where(
            and_(
                ListingDB.id == expected_listing_dict["id"],
                MarketDB.id == expected_listing_dict["market_id"],
            )
        )
    ).scalar_one()

    assert result.id == expected_listing_dict["id"]
    assert result.adr_usd == expected_listing_dict["adr_usd"]
    assert result.airroi_id == expected_listing_dict["airroi_id"]
    assert result.annual_revenue_usd == expected_listing_dict["annual_revenue_usd"]
    assert result.bedrooms == expected_listing_dict["bedrooms"]
    assert result.latitude == expected_listing_dict["latitude"]
    assert isinstance(result.location, WKBElement)
    # NOTE: Revisit this when you figure out how the hell to interact with thes columns lol
    # assert result.location == expected_listing_dict["location"]
    # result_geog = ST_GeogFromWKB(result.location)
    # from rich import inspect as ri

    # ri(result_geog, methods=True)
    # breakpoint()
    # assert result.location == WKTElement(expected_listing_dict["location"], srid=4326)
    assert result.longitude == expected_listing_dict["longitude"]
    assert result.market_id == expected_listing_dict["market_id"]
    assert result.occupancy_rate == expected_listing_dict["occupancy_rate"]
    assert result.property_type == expected_listing_dict["property_type"]
    assert result.source_url == expected_listing_dict["source_url"]
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
