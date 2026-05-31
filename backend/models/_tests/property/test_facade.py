from __future__ import annotations

from datetime import datetime

import pytest

from models.property.entity import PropertyEntity
from models.property.facade import PropertyFacade


class TestPropertyFacade:
    @pytest.fixture
    def property_facade(self, test_db_session):
        return PropertyFacade(db_session=test_db_session)

    def _compare_result_with_expected(
        self, result: PropertyEntity, expected_dict: dict
    ):
        for key, value in expected_dict.items():
            if key == "source_created_at":
                expected_dt = datetime.fromisoformat(value).replace(tzinfo=None)
                assert result.source_created_at == expected_dt
            else:
                assert getattr(result, key) == value

        return True

    def test_get_one_by_id(self, property_facade, property_record):
        result = property_facade.get_one_by_id(property_record.id)
        assert result == PropertyEntity.model_validate(property_record)

    def test_get_one_by_id_no_result(self, property_facade):
        with pytest.raises(PropertyFacade.NoResultFound):
            non_existent_id = "988d0b5d-d4a5-4808-a94d-2d9df1df7588"
            property_facade.get_one_by_id(non_existent_id)

    def test_create_or_update_creates_new_record(
        self, property_facade, expected_property_dict
    ):
        result = property_facade.create_or_update(payload=expected_property_dict)

        assert self._compare_result_with_expected(result, expected_property_dict)

    def test_create_or_update_updates_existing_record(
        self, property_facade, property_record
    ):
        property_entity = PropertyEntity.model_validate(property_record)
        property_record_dict = property_entity.model_dump()
        updated_payload = {
            **property_record_dict,
            "source_created_at": property_entity.source_created_at.isoformat(),
            "bedrooms": property_record_dict["bedrooms"] + 1,
        }

        result = property_facade.create_or_update(payload=updated_payload)

        assert self._compare_result_with_expected(result, updated_payload)
        assert result.bedrooms != property_record_dict["bedrooms"]
