from __future__ import annotations

import pytest
from sqlalchemy.orm import Session

from _factories.market.db import MarketDBFactory
from api.routes.markets import read_markets_list
from models.market.entity import MarketEntity
from models.market.facade import MarketFacade


class TestReadMarketsListRoute:
    @pytest.fixture
    def market_facade(self, test_db_session: Session):
        return MarketFacade(db_session=test_db_session)

    @pytest.fixture
    def patch_route_db_session(self, monkeypatch, test_db_session: Session) -> None:
        class MockDBSessionManager:
            def scoped_session(self):
                return test_db_session

        monkeypatch.setattr("api.routes.markets.DBSessionManager", MockDBSessionManager)

    def test_returns_all_markets(
        self, patch_route_db_session, test_db_session: Session
    ):
        market_zipaquira = MarketDBFactory(locality="Zipaquira")
        market_bogota = MarketDBFactory(locality="Bogota")
        market_medellin = MarketDBFactory(locality="Medellin")
        test_db_session.commit()

        result = read_markets_list()

        assert result == {
            "data": [
                MarketEntity.model_validate(market_bogota),
                MarketEntity.model_validate(market_medellin),
                MarketEntity.model_validate(market_zipaquira),
            ]
        }

    def test_returns_no_markets(self, patch_route_db_session):
        result = read_markets_list()

        assert result == {"data": []}
