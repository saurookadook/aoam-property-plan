from __future__ import annotations

import pytest

from _factories.listing.db import ListingDBFactory
from _factories.market.db import MarketDBFactory
from models.listing.entity import ListingEntity, format_wkt_coordinate
from models.listing.facade import ListingFacade


class TestFormatWktCoordinate:
    @pytest.mark.parametrize(
        "data_val, expected",
        [
            # whole numbers lose the trailing `.0` - the case that made
            # `test_get_all_by_market_id` flaky
            (36.0, "36"),
            (100.0, "100"),
            (90, "90"),
            # fractional coordinates are left alone
            (36.25, "36.25"),
            (139.55722, "139.55722"),
            (-75.640629, "-75.640629"),
            (4.57076, "4.57076"),
            # never scientific notation
            (1e-07, "0.0000001"),
            # at most 15 significant digits
            (0.30000000000000004, "0.3"),
            # zero has no sign
            (0.0, "0"),
            (-0.0, "0"),
            # strings and Decimals are accepted, as `location_on_land` yields strings
            ("36.0000", "36"),
            ("139.55722", "139.55722"),
        ],
    )
    def test_matches_postgis_st_astext_rendering(self, data_val, expected):
        assert format_wkt_coordinate(data_val) == expected


class TestListingEntityLocation:
    @pytest.mark.parametrize("latitude", [36.0, 36.25])
    def test_built_location_matches_db_roundtrip(self, latitude, test_db_session):
        """
        `ListingFacade` reads `location` back via `ST_AsText`, so a WKT POINT built
        from a (lat, lng) pair must render identically - otherwise comparing a
        constructed entity to a fetched one fails on whole-number coordinates.
        """
        market = MarketDBFactory()
        test_db_session.commit()

        longitude = 139.55722

        built_location = ListingEntity.model_validate(
            {
                "id": "3f9f1d2e-9d0a-4a5a-9d1b-2f6c8e4b1a77",
                "created_at": "2026-04-20T11:15:00+00:00",
                "updated_at": "2026-04-20T11:15:00+00:00",
                "airroi_id": 999999,
                "bedrooms": 1,
                "latitude": latitude,
                "longitude": longitude,
                "location": (latitude, longitude),
                "property_type": "house",
            }
        ).location

        listing_record = ListingDBFactory(
            market_id=market.id,
            latitude=latitude,
            longitude=longitude,
            location=f"POINT({longitude} {latitude})",
        )
        test_db_session.commit()

        fetched_location = (
            ListingFacade(db_session=test_db_session)
            .get_one_by_id(listing_record.id)
            .location
        )

        assert built_location == fetched_location
