from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID

import factory
import pytest
from sqlalchemy import select, and_

from _factories.property.db import PropertyDBFactory
from models.property.db import PropertyDB


@pytest.fixture
def expected_property_dict(mock_utcnow):
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
        source_created_at=(mock_utcnow - timedelta(days=30))
        .replace(tzinfo=timezone.utc)
        .isoformat(),
        source_url="https://example.com/property/12345",
        state="Test State",
    )


def test_property_db(expected_property_dict, mock_utcnow, test_db_session):
    property_record = PropertyDBFactory(**expected_property_dict)

    test_db_session.commit()

    result = test_db_session.execute(
        select(PropertyDB).where(
            and_(
                PropertyDB.id == expected_property_dict["id"],
                PropertyDB.city == expected_property_dict["city"],
            )
        )
    ).scalar_one()

    assert result.id == expected_property_dict["id"]
    assert result.address == expected_property_dict["address"]
    assert result.bedrooms == expected_property_dict["bedrooms"]
    assert result.city == expected_property_dict["city"]
    assert result.country == expected_property_dict["country"]
    assert result.latitude == expected_property_dict["latitude"]
    assert result.longitude == expected_property_dict["longitude"]
    assert result.neighborhood == expected_property_dict["neighborhood"]
    assert result.notes == expected_property_dict["notes"]
    assert result.postal_code == expected_property_dict["postal_code"]
    assert result.property_type == expected_property_dict["property_type"]
    assert result.purchase_price_cop == expected_property_dict["purchase_price_cop"]
    assert result.purchase_price_usd == expected_property_dict["purchase_price_usd"]
    assert result.source_url == expected_property_dict["source_url"]
    assert result.state == expected_property_dict["state"]
    assert (
        result.source_created_at.replace(tzinfo=timezone.utc).isoformat()
        == expected_property_dict["source_created_at"]
    )
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
