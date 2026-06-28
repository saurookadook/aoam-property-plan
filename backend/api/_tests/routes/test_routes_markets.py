from __future__ import annotations

import pytest
from fastapi import status
from sqlalchemy.orm import Session

from _factories.listing.db import ListingDBFactory
from _factories.listing.entity import ListingEntityFactory
from _factories.market.db import MarketDBFactory
from models.listing.entity import ListingEntity
from models.market.entity import MarketEntity
from models.market.facade import MarketFacade


@pytest.fixture
def market_facade(test_db_session: Session):
    return MarketFacade(db_session=test_db_session)


class TestReadMarketsListRoute:
    def test_returns_all_markets(self, test_app_client, test_db_session: Session):
        market_zipaquira = MarketDBFactory(locality="Zipaquira")
        market_bogota = MarketDBFactory(locality="Bogota")
        market_medellin = MarketDBFactory(locality="Medellin")
        test_db_session.commit()

        result = test_app_client.get("/api/markets")

        assert result.status_code == 200
        assert result.json() == {
            "data": [
                MarketEntity.model_validate(market_bogota).model_dump(mode="json"),
                MarketEntity.model_validate(market_medellin).model_dump(mode="json"),
                MarketEntity.model_validate(market_zipaquira).model_dump(mode="json"),
            ]
        }

    def test_returns_no_markets(self, test_app_client):
        result = test_app_client.get("/api/markets")

        assert result.status_code == 200
        assert result.json() == {"data": []}


class TestReadMarketOverviewRoute:
    def test_returns_market_and_listings(
        self, test_app_client, test_db_session: Session
    ):
        market = MarketDBFactory()
        test_db_session.commit()

        listings = [ListingEntityFactory(market_id=market.id) for _ in range(2)]
        for listing in listings:
            ListingDBFactory(**listing.model_dump())
        test_db_session.commit()

        result = test_app_client.get(f"/api/markets/{market.id}")

        assert result.status_code == 200
        assert result.json() == {
            "data": {
                "market": MarketEntity.model_validate(market).model_dump(mode="json"),
                "listings": [
                    ListingEntity.model_validate(listing).model_dump(mode="json")
                    for listing in listings
                ],
            }
        }

    def test_returns_market_but_no_listings(
        self, test_app_client, test_db_session: Session
    ):
        market = MarketDBFactory()
        test_db_session.commit()

        result = test_app_client.get(f"/api/markets/{market.id}")

        assert result.status_code == 200
        assert result.json() == {
            "data": {
                "market": MarketEntity.model_validate(market).model_dump(mode="json"),
                "listings": [],
            }
        }

    def test_raises_http_exception_for_nonexistent_market(
        self, test_app_client, test_db_session: Session
    ):
        non_existent_market_id = "01d336ff-c742-4682-80bb-5f7d5cdf8d26"

        result = test_app_client.get(f"/api/markets/{non_existent_market_id}")
        assert result.status_code == status.HTTP_404_NOT_FOUND
        assert result.json() == {"detail": "Market not found"}
