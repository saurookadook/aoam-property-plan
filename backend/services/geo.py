"""
Distance between two coordinates, in kilometres.

Pure and dependency-free, like ``services.calculations``: no DB session, no
network. That is the point of it being here rather than in SQL. A comp's distance
is computed while the AirROI payload is being turned into rows, before any
``listings`` record for it necessarily exists - there is nothing to run
``ST_Distance`` against yet, and doing it in Postgres would mean a round trip per
comp to learn something the response already contains. The ``ix_listings_location``
GiST index earns its keep on radius *searches* over the whole table; it buys
nothing for measuring 25 points against one.

Haversine treats the Earth as a sphere, so it runs about 0.5% off a proper
ellipsoidal (Vincenty/geodesic) distance at worst. On a comp set inside a 10km
radius that is tens of metres - far below the resolution at which "how far is
this comparable" means anything.
"""

from __future__ import annotations

from math import asin, cos, radians, sin, sqrt

EARTH_RADIUS_KM = 6371.0088
"""
The IUGG mean radius. Any figure between the polar 6357 and equatorial 6378 is
defensible; the mean keeps the error symmetric rather than biasing every comp in
one direction.
"""


def haversine_km(lat_a: float, lng_a: float, lat_b: float, lng_b: float) -> float:
    """
    Great-circle distance between two points given in decimal degrees.

    NOTE: takes floats, not optionals. AirROI usually gives a comp
    ``location_info.latitude/longitude``, but ``property_comps.distance_km`` is
    nullable for the case where it does not - and the caller is the only one that
    can tell a missing coordinate from a real ``0.0``, which is what a comp
    sitting on the property itself measures.
    """
    lat_a_rad, lat_b_rad = radians(lat_a), radians(lat_b)
    delta_lat = lat_b_rad - lat_a_rad
    delta_lng = radians(lng_b) - radians(lng_a)

    # The ``asin(sqrt(h))`` form rather than ``acos``: for two points a few
    # hundred metres apart the cosine of the angle rounds to 1.0 in float64 and
    # the distance collapses to zero. Haversine stays accurate at that scale,
    # which is the scale a comp set lives at.
    h = (
        sin(delta_lat / 2) ** 2
        + cos(lat_a_rad) * cos(lat_b_rad) * sin(delta_lng / 2) ** 2
    )

    return 2 * EARTH_RADIUS_KM * asin(sqrt(h))
