from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID

import factory
import pytest
from sqlalchemy import select

from _factories.exchange_rate.db import ExchangeRateDBFactory
from models.exchange_rate.db import ExchangeRateDB


@pytest.fixture
def expected_exchange_rate_dict(mock_utcnow):
    record_date = (
        (mock_utcnow - timedelta(days=1))
        .replace(tzinfo=timezone.utc)
        .date()
        .isoformat()
    )

    return dict(
        id=UUID("5fd8ed45-5c16-47ab-b625-2cd37cc1f1a6"),
        record_date=record_date,
        cop_per_usd=500.0,
    )


def test_exchange_rate_db(expected_exchange_rate_dict, mock_utcnow, test_db_session):
    exchange_rate = ExchangeRateDBFactory(**expected_exchange_rate_dict)
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
