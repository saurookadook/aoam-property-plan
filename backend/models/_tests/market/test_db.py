from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select, and_

from _factories.market.db import MarketDBFactory
from models.market.db import MarketDB


def test_market_db(expected_market_dict, mock_utcnow, test_db_session):
    MarketDBFactory(**expected_market_dict)
    test_db_session.commit()

    result = test_db_session.execute(
        select(MarketDB).where(
            and_(
                MarketDB.country == expected_market_dict["country"],
                MarketDB.locality == expected_market_dict["locality"],
            )
        )
    ).scalar_one()

    assert isinstance(result.id, UUID)
    assert result.country == expected_market_dict["country"]
    assert result.district == expected_market_dict["district"]
    assert result.locality == expected_market_dict["locality"]
    assert result.region == expected_market_dict["region"]
    # assert result.peak_months == expected_market_dict["peak_months"]
    # assert result.last_updated.isoformat() == expected_market_dict["last_updated"]
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
