from __future__ import annotations

import pytest

from _factories.market.db import MarketDBFactory
from models.market.entity import MarketEntity
from models.market.facade import MarketFacade


class TestMarketFacade:
    @pytest.fixture
    def market_facade(self, test_db_session):
        return MarketFacade(db_session=test_db_session)

    @pytest.fixture
    def market_record(self, expected_market_dict, test_db_session):
        market = MarketDBFactory(**expected_market_dict)
        test_db_session.commit()
        return market

    def test_get_one_by_id(self, market_facade, market_record):
        result = market_facade.get_one_by_id(market_record.id)
        assert result == MarketEntity.model_validate(market_record)

    def test_get_one_by_id_no_result(self, market_facade):
        with pytest.raises(MarketFacade.NoResultFound):
            non_existent_id = "988d0b5d-d4a5-4808-a94d-2d9df1df7588"
            market_facade.get_one_by_id(non_existent_id)
