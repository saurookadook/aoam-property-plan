from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

import pytest
from sqlalchemy import and_, select
from sqlalchemy.exc import IntegrityError

from _factories.property_comp.db import PropertyCompDBFactory
from models.property_comp.db import PropertyCompDB


def test_property_comp_db(expected_property_comp_dict, mock_utcnow, test_db_session):
    PropertyCompDBFactory(**expected_property_comp_dict)
    test_db_session.commit()

    result = test_db_session.execute(
        select(PropertyCompDB).where(
            and_(
                PropertyCompDB.property_id
                == expected_property_comp_dict["property_id"],
                PropertyCompDB.listing_id == expected_property_comp_dict["listing_id"],
            )
        )
    ).scalar_one()

    assert result.id == expected_property_comp_dict["id"]
    assert result.property_id == expected_property_comp_dict["property_id"]
    assert result.listing_id == expected_property_comp_dict["listing_id"]
    # ``NUMERIC`` comes back off the row as a ``Decimal``; only the entity
    # coerces it to ``float``.
    assert float(result.adr_cop) == pytest.approx(
        expected_property_comp_dict["adr_cop"]
    )
    assert result.distance_km == pytest.approx(
        expected_property_comp_dict["distance_km"]
    )
    assert result.occupancy_rate == pytest.approx(
        expected_property_comp_dict["occupancy_rate"]
    )
    assert float(result.ttm_revenue_cop) == pytest.approx(
        expected_property_comp_dict["ttm_revenue_cop"]
    )
    assert result.ttm_total_days == expected_property_comp_dict["ttm_total_days"]
    assert result.captured_at.isoformat() == expected_property_comp_dict["captured_at"]
    # ``captured_at`` is ``TIMESTAMP(timezone=True)``, unlike the naive column
    # ``property_financial_reports.calculated_at`` shipped with.
    assert result.captured_at.tzinfo is not None

    assert isinstance(result.created_at, datetime)
    assert isinstance(result.updated_at, datetime)
    assert (
        result.created_at.replace(tzinfo=timezone.utc).isoformat()
        == mock_utcnow.isoformat()
    )


def test_property_comp_db_is_unique_per_property_and_listing(
    expected_property_comp_dict, test_db_session
):
    PropertyCompDBFactory(**expected_property_comp_dict)
    test_db_session.commit()

    # A second run against the same property mints a fresh ``id`` for a comp
    # already on file; only ``property_comps_property_id_listing_id_key`` stops
    # it becoming a duplicate row.
    PropertyCompDBFactory(
        **{**expected_property_comp_dict, "id": uuid4(), "adr_cop": 999_999.0}
    )

    with pytest.raises(IntegrityError):
        test_db_session.commit()

    test_db_session.rollback()
