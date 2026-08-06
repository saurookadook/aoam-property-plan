from __future__ import annotations

from collections import deque
from datetime import date, datetime, timezone
from uuid import UUID

import pytest
from sqlalchemy.orm import Session

from _factories.listing.db import ListingDBFactory
from _factories.listing.entity import ListingEntityFactory
from _factories.listing_financial_report.db import ListingFinancialReportDBFactory
from _factories.market.db import MarketDBFactory
from _factories.market.entity import MarketEntityFactory
from api.routes.handlers.home import get_highest_earners
from models.listing.entity import ListingEntity, HighestEarningListingEntity
from models.listing_financial_report.entity import ListingFinancialReportEntity


def test_get_highest_earners(test_db_session: Session):
    today = date.today()
    today_now = datetime(
        year=today.year,
        month=today.month,
        day=today.day,
        hour=13,
        minute=30,
        tzinfo=timezone.utc,
    )

    market_entity = MarketEntityFactory()
    MarketDBFactory(**market_entity.model_dump())
    test_db_session.commit()

    expected_earners: deque[HighestEarningListingEntity] = deque()

    for i in range(10):
        listing_entity = ListingEntityFactory(
            created_at=today_now, market_id=market_entity.id, updated_at=today_now
        )
        ListingDBFactory(**listing_entity.model_dump())
        test_db_session.commit()

        financial_report_records = [
            ListingFinancialReportDBFactory(
                listing_id=listing_entity.id, ttm_revenue=1000 * (i + 1)
            )
            for _ in range(2)
        ]
        test_db_session.commit()

        listing_dict = dict(listing_entity.__dict__)

        expected_earner_entity = HighestEarningListingEntity(
            created_at=listing_dict["created_at"],
            cover_photo_url=listing_dict["cover_photo_url"],
            id=listing_dict["id"],
            market_id=listing_dict["market_id"],
            name=listing_dict["name"],
            ttm_revenue=financial_report_records[-1].ttm_revenue,
            updated_at=listing_dict["updated_at"],
            country=market_entity.country,
            locality=market_entity.locality,
            region=market_entity.region,
        )

        expected_earners.appendleft(expected_earner_entity)

        if len(expected_earners) > 3:
            expected_earners.pop()

    results = get_highest_earners(db_session=test_db_session)

    assert len(results) == 3
    for listing_result, expected_earner in zip(results, expected_earners):
        assert expected_earner.id == listing_result.id
        assert expected_earner.cover_photo_url == listing_result.cover_photo_url
        assert expected_earner.market_id == listing_result.market_id
        assert expected_earner.name == listing_result.name
        assert expected_earner.ttm_revenue == listing_result.ttm_revenue
        assert expected_earner.country == listing_result.country
        assert expected_earner.locality == listing_result.locality
        assert expected_earner.region == listing_result.region
