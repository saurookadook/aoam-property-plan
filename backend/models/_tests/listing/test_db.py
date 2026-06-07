from __future__ import annotations

from datetime import datetime, timezone

from geoalchemy2.elements import WKBElement
from sqlalchemy import and_, select

from _factories.listing.db import ListingDBFactory
from models.listing.db import ListingDB
from models.market.db import MarketDB


def test_listing_db(expected_listing_dict, mock_utcnow, test_db_session):
    ListingDBFactory(**expected_listing_dict)
    test_db_session.commit()

    result = test_db_session.execute(
        select(ListingDB)
        .join(MarketDB, ListingDB.market_id == MarketDB.id)
        .where(
            and_(
                ListingDB.id == expected_listing_dict["id"],
                MarketDB.id == expected_listing_dict["market_id"],
            )
        )
    ).scalar_one()

    assert result.id == expected_listing_dict["id"]
    assert result.airroi_id == expected_listing_dict["airroi_id"]
    assert result.bedrooms == expected_listing_dict["bedrooms"]
    assert result.latitude == expected_listing_dict["latitude"]
    assert isinstance(result.location, WKBElement)
    # NOTE: Revisit this when you figure out how the hell to interact with thes columns lol
    # assert result.location == expected_listing_dict["location"]
    assert result.longitude == expected_listing_dict["longitude"]
    assert result.market_id == expected_listing_dict["market_id"]
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
