from __future__ import annotations

from datetime import datetime, timedelta

import pytest
from sqlalchemy import func, select

from _factories.property.db import PropertyDBFactory
from models.property.db import PropertyDB
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

    def test_get_all_returns_newest_first(
        self, property_facade, property_record, test_db_session
    ):
        older = PropertyDBFactory(
            created_at=property_record.created_at - timedelta(days=1),
            source_url="https://example.com/property/older",
        )
        newer = PropertyDBFactory(
            created_at=property_record.created_at + timedelta(days=1),
            source_url="https://example.com/property/newer",
        )
        test_db_session.commit()

        results = property_facade.get_all()

        assert [record.id for record in results] == [
            newer.id,
            property_record.id,
            older.id,
        ]

    def test_get_all_is_empty_when_nothing_is_stored(self, property_facade):
        assert property_facade.get_all() == []

    def test_get_one_by_source_url(self, property_facade, property_record):
        result = property_facade.get_one_by_source_url(property_record.source_url)
        assert result == PropertyEntity.model_validate(property_record)

    def test_get_one_by_source_url_no_result(self, property_facade):
        with pytest.raises(PropertyFacade.NoResultFound):
            non_existent_source_url = "https://example.com/property/does-not-exist"
            property_facade.get_one_by_source_url(non_existent_source_url)

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

    def test_create_or_update_updates_existing_record_by_source_url(
        self, property_facade, property_record, test_db_session
    ):
        """
        A re-scrape of the same listing has no ``id`` to match on, so the existing
        record must be found via ``source_url`` and updated in place.
        """
        property_entity = PropertyEntity.model_validate(property_record)
        updated_payload = {
            "source_url": property_entity.source_url,
            "purchase_price_cop": property_entity.purchase_price_cop + 50000000,
        }

        result = property_facade.create_or_update(payload=updated_payload)

        assert result.id == property_record.id
        assert result.purchase_price_cop == updated_payload["purchase_price_cop"]
        assert result.purchase_price_cop != property_entity.purchase_price_cop

    def test_create_or_update_does_not_duplicate_by_source_url(
        self, property_facade, property_record, test_db_session
    ):
        """
        Re-POSTing the same listing URL must not insert a second row - this is what
        the ``properties_source_url_key`` unique constraint protects.
        """
        source_url = property_record.source_url

        for bedrooms in (4, 5):
            property_facade.create_or_update(
                payload={"source_url": source_url, "bedrooms": bedrooms}
            )

        row_count = test_db_session.execute(
            select(func.count())
            .select_from(PropertyDB)
            .where(PropertyDB.source_url == source_url)
        ).scalar_one()

        assert row_count == 1

    def test_create_or_update_creates_new_record_without_id(
        self, property_facade, expected_property_dict, test_db_session
    ):
        """
        An unseen ``source_url`` with no ``id`` falls through both lookups and
        inserts, relying on the ``uuid4`` column default for the primary key.
        """
        payload = {
            key: value
            for key, value in expected_property_dict.items()
            if key not in ("id", "source_created_at")
        }
        payload["source_url"] = "https://example.com/property/67890"
        payload["source_created_at"] = expected_property_dict["source_created_at"]

        result = property_facade.create_or_update(payload=payload)

        assert result.id is not None
        assert result.source_url == payload["source_url"]
