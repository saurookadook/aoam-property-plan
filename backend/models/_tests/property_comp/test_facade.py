from __future__ import annotations

from datetime import datetime
from uuid import uuid4

import pytest

from _factories.listing.db import ListingDBFactory
from _factories.property_comp.db import PropertyCompDBFactory
from models.property_comp.entity import PropertyCompEntity
from models.property_comp.facade import PropertyCompFacade


class TestPropertyCompFacade:
    @pytest.fixture
    def property_comp_facade(self, test_db_session):
        return PropertyCompFacade(db_session=test_db_session)

    def _compare_result_with_expected(
        self, result: PropertyCompEntity, expected_dict: dict
    ):
        for key, value in expected_dict.items():
            # ``captured_at`` alone arrives as an ISO string rather than a
            # datetime, so it is compared parsed. The offset it carries is
            # significant - the column is ``TIMESTAMP(timezone=True)``.
            if key == "captured_at":
                assert result.captured_at == datetime.fromisoformat(value)
            elif isinstance(value, (int, float)):
                assert getattr(result, key) == pytest.approx(value)
            else:
                assert getattr(result, key) == value

        return True

    def test_get_one_by_id(self, property_comp_facade, property_comp_record):
        result = property_comp_facade.get_one_by_id(property_comp_record.id)

        assert result == PropertyCompEntity.model_validate(property_comp_record)

    def test_get_one_by_id_no_result(self, property_comp_facade):
        with pytest.raises(PropertyCompFacade.NoResultFound):
            property_comp_facade.get_one_by_id("988d0b5d-d4a5-4808-a94d-2d9df1df7588")

    def test_get_one_by_property_id_and_listing_id(
        self, property_comp_facade, property_comp_record
    ):
        result = property_comp_facade.get_one_by_property_id_and_listing_id(
            property_id=property_comp_record.property_id,
            listing_id=property_comp_record.listing_id,
        )

        assert result.id == property_comp_record.id

    def test_get_one_by_property_id_and_listing_id_no_result(
        self, property_comp_facade, property_comp_record
    ):
        with pytest.raises(PropertyCompFacade.NoResultFound):
            property_comp_facade.get_one_by_property_id_and_listing_id(
                property_id=property_comp_record.property_id,
                listing_id="988d0b5d-d4a5-4808-a94d-2d9df1df7588",
            )

    def test_get_all_by_property_id(
        self, property_comp_facade, property_comp_record, property_record
    ):
        results = property_comp_facade.get_all_by_property_id(property_record.id)

        assert [comp.id for comp in results] == [property_comp_record.id]

    def test_get_all_by_property_id_sorts_nearest_first_with_nulls_last(
        self,
        property_comp_facade,
        property_record,
        test_market_record,
        test_db_session,
    ):
        listings = [
            ListingDBFactory(
                market_id=test_market_record.id,
                latitude=latitude,
                longitude=longitude,
                location=f"POINT({longitude} {latitude})",
            )
            for latitude, longitude in ((1.0, 2.0), (3.0, 4.0), (5.0, 6.0))
        ]
        test_db_session.commit()

        # Postgres sorts nulls *first* under ``ASC`` for a reason that does not
        # apply here: a comp with no coordinates is not the nearest one.
        further, nearer, no_distance = (
            PropertyCompDBFactory(
                property_id=property_record.id,
                listing_id=listing.id,
                distance_km=distance_km,
            )
            for listing, distance_km in zip(listings, (9.0, 1.0, None))
        )
        test_db_session.commit()

        results = property_comp_facade.get_all_by_property_id(property_record.id)

        assert [comp.id for comp in results] == [
            nearer.id,
            further.id,
            no_distance.id,
        ]

    def test_get_all_by_property_id_carries_the_listing(
        self,
        listing_record,
        property_comp_facade,
        property_comp_record,
        property_record,
    ):
        comp = property_comp_facade.get_all_by_property_id(property_record.id)[0]

        assert comp.listing is not None
        assert comp.listing.id == listing_record.id
        assert comp.listing.airroi_id == listing_record.airroi_id
        assert comp.listing.property_type == listing_record.property_type

    def test_get_all_by_property_id_serves_a_narrow_listing(
        self, property_comp_facade, property_record, property_comp_record
    ):
        comp = property_comp_facade.get_all_by_property_id(property_record.id)[0]

        # The comp table renders a name, a type and a link out - not a
        # description, thirteen amenities and twenty photo URLs per row.
        assert set(comp.listing.model_dump()) == {
            "id",
            "airroi_id",
            "baths",
            "bedrooms",
            "cover_photo_url",
            "latitude",
            "longitude",
            "name",
            "property_type",
            "source_url",
        }

    def test_the_write_path_entity_has_no_listing_key(
        self, property_comp_facade, property_comp_record
    ):
        # ``PropertyCompEntity`` stays relationship-free so that round-tripping
        # one through ``model_dump()`` still produces a usable payload.
        written = property_comp_facade.get_one_by_id(property_comp_record.id)

        assert "listing" not in written.model_dump()

    def test_get_all_by_property_id_is_empty_for_an_unanalysed_property(
        self, property_comp_facade, property_record
    ):
        assert property_comp_facade.get_all_by_property_id(property_record.id) == []

    def test_create_or_update_creates_new_record(
        self, property_comp_facade, expected_property_comp_dict
    ):
        result = property_comp_facade.create_or_update(
            payload=expected_property_comp_dict
        )

        assert self._compare_result_with_expected(result, expected_property_comp_dict)

    def test_create_or_update_updates_existing_record(
        self, property_comp_facade, property_comp_record
    ):
        payload = {
            **PropertyCompEntity.model_validate(property_comp_record).model_dump(),
            "adr_cop": 500_000.0,
        }

        result = property_comp_facade.create_or_update(payload=payload)

        assert result.id == property_comp_record.id
        assert result.adr_cop == pytest.approx(500_000.0)

    def test_create_or_update_upserts_on_the_property_and_listing_pair(
        self, property_comp_facade, expected_property_comp_dict, property_record
    ):
        created = property_comp_facade.create_or_update(
            payload=expected_property_comp_dict
        )

        # Re-analysing a property mints a fresh ``id`` for a comp already on
        # file. Matching only on ``id`` would take the insert path and collide
        # with ``property_comps_property_id_listing_id_key``.
        updated = property_comp_facade.create_or_update(
            payload={
                **expected_property_comp_dict,
                "id": uuid4(),
                "adr_cop": 600_000.0,
            }
        )

        assert updated.id == created.id
        assert updated.adr_cop == pytest.approx(600_000.0)
        assert len(property_comp_facade.get_all_by_property_id(property_record.id)) == 1

    def test_update(self, property_comp_facade, property_comp_record):
        result = property_comp_facade.update(
            payload={"id": property_comp_record.id, "distance_km": 7.5}
        )

        assert result.distance_km == pytest.approx(7.5)
