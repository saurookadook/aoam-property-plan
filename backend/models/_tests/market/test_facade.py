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

    def _compare_result_with_expected(self, result: MarketEntity, expected_dict: dict):
        for key, value in expected_dict.items():
            assert getattr(result, key) == value

        return True

    def test_get_one_by_id(self, market_facade, market_record):
        result = market_facade.get_one_by_id(market_record.id)
        assert result == MarketEntity.model_validate(market_record)

    def test_get_one_by_id_no_result(self, market_facade):
        with pytest.raises(MarketFacade.NoResultFound):
            non_existent_id = "988d0b5d-d4a5-4808-a94d-2d9df1df7588"
            market_facade.get_one_by_id(non_existent_id)

    def test_create_or_update_creates_new_record(
        self, market_facade, expected_market_dict
    ):
        result = market_facade.create_or_update(payload=expected_market_dict)

        assert self._compare_result_with_expected(result, expected_market_dict)

    def test_create_or_update_updates_existing_record(
        self,
        market_facade,
        market_record,
    ):
        market_entity = MarketEntity.model_validate(market_record)
        market_record_dict = market_entity.model_dump()
        updated_payload = {
            **market_record_dict,
            "region": "Updated Region",
        }

        result = market_facade.create_or_update(payload=updated_payload)

        assert self._compare_result_with_expected(result, updated_payload)
        assert result.region != market_record_dict["region"]
