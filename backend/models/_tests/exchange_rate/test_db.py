from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select

from models.exchange_rate.db import ExchangeRateDB


def test_exchange_rate_db(expected_exchange_rate_dict, mock_utcnow, test_db_session):
    from _factories.exchange_rate.db import ExchangeRateDBFactory

    ExchangeRateDBFactory(**expected_exchange_rate_dict)
    test_db_session.commit()

    result = test_db_session.execute(
        select(ExchangeRateDB).where(
            ExchangeRateDB.record_date == expected_exchange_rate_dict["record_date"],
        )
    ).scalar_one()

    assert result.id == expected_exchange_rate_dict["id"]
    assert result.record_date.isoformat() == expected_exchange_rate_dict["record_date"]
    assert result.cop_per_usd == expected_exchange_rate_dict["cop_per_usd"]
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
