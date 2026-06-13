from __future__ import annotations

from uuid import UUID

import pytest

from _factories.listing.db import ListingDBFactory
from models.listing.entity import ListingEntity
from models.listing.facade import ListingFacade


class TestListingFacade:
    @pytest.fixture
    def listing_facade(self, test_db_session):
        return ListingFacade(db_session=test_db_session)

    @pytest.fixture
    def listing_record(self, expected_listing_dict, test_db_session):
        listing = ListingDBFactory(**expected_listing_dict)
        test_db_session.commit()
        return listing

    def _compare_result_with_expected(self, result: ListingEntity, expected_dict: dict):
        for key, value in expected_dict.items():
            assert getattr(result, key) == value

        return True

    def test_get_one_by_id(self, listing_facade, listing_record, expected_listing_dict):
        result = listing_facade.get_one_by_id(listing_record.id)

        assert self._compare_result_with_expected(result, expected_listing_dict)

    def test_get_one_by_id_no_result(self, listing_facade):
        with pytest.raises(ListingFacade.NoResultFound):
            non_existent_id = UUID("988d0b5d-d4a5-4808-a94d-2d9df1df7588")
            listing_facade.get_one_by_id(non_existent_id)

    def test_create_or_update_creates_new_record(
        self, listing_facade, expected_listing_dict
    ):
        result = listing_facade.create_or_update(payload=expected_listing_dict)

        assert self._compare_result_with_expected(result, expected_listing_dict)

    def test_create_or_update_creates_new_record_no_id(
        self, listing_facade, expected_listing_dict
    ):
        del expected_listing_dict["id"]
        result = listing_facade.create_or_update(payload=expected_listing_dict)

        assert self._compare_result_with_expected(result, expected_listing_dict)

    def test_create_or_update_updates_existing_record(
        self, listing_facade, listing_record, expected_listing_dict
    ):
        updated_payload = {
            **expected_listing_dict,
            "id": listing_record.id,
            "airroi_id": listing_record.airroi_id,
            "bedrooms": expected_listing_dict["bedrooms"] + 1,
        }

        result = listing_facade.create_or_update(payload=updated_payload)

        assert self._compare_result_with_expected(result, updated_payload)
        assert result.bedrooms != expected_listing_dict["bedrooms"]
