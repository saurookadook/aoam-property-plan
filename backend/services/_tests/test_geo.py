from __future__ import annotations

import pytest

from services.geo import EARTH_RADIUS_KM, haversine_km

BOGOTA = (4.7110, -74.0721)
SALENTO = (4.6375, -75.5703)


class TestHaversineKm:
    def test_identical_points_are_zero(self):
        assert haversine_km(*SALENTO, *SALENTO) == 0.0

    def test_known_distance(self):
        # Cross-checked against PostGIS ``ST_Distance`` over ``geography``, which
        # is a proper WGS84 geodesic: 166.426 km. Haversine treats the Earth as a
        # sphere, so it lands ~0.1% under.
        assert haversine_km(*BOGOTA, *SALENTO) == pytest.approx(166.24, abs=0.01)
        assert haversine_km(*BOGOTA, *SALENTO) == pytest.approx(166.426, rel=0.006)

    def test_is_symmetric(self):
        assert haversine_km(*BOGOTA, *SALENTO) == haversine_km(*SALENTO, *BOGOTA)

    @pytest.mark.parametrize(
        "lat_a, lng_a, lat_b, lng_b, geodesic_km",
        [
            # One degree along the equator, and one along a meridian. The sphere
            # model cannot get both right; both stay inside 0.6%.
            (0.0, 0.0, 0.0, 1.0, 111.319),
            (0.0, 0.0, 1.0, 0.0, 110.574),
        ],
    )
    def test_stays_within_the_spherical_error_budget(
        self, lat_a, lng_a, lat_b, lng_b, geodesic_km
    ):
        assert haversine_km(lat_a, lng_a, lat_b, lng_b) == pytest.approx(
            geodesic_km, rel=0.006
        )

    def test_short_distances_do_not_collapse_to_zero(self):
        # The reason for the ``asin(sqrt(h))`` form: with the spherical law of
        # cosines, ``cos`` of this angle rounds to 1.0 in float64 and the whole
        # distance disappears. A comp set lives at exactly this scale.
        result = haversine_km(4.6375, -75.5703, 4.63840, -75.5703)

        assert result == pytest.approx(0.1, abs=0.001)
        assert result > 0

    def test_antipodal_points_are_half_the_circumference(self):
        assert haversine_km(0.0, 0.0, 0.0, 180.0) == pytest.approx(
            EARTH_RADIUS_KM * 3.141592653589793, rel=1e-9
        )

    def test_negative_coordinates_are_handled(self):
        # Both test coordinates are in the western hemisphere; a sign error would
        # show up as a wildly wrong magnitude rather than a small one.
        assert haversine_km(-4.6375, -75.5703, 4.6375, -75.5703) == pytest.approx(
            1030.9, abs=1.0
        )
