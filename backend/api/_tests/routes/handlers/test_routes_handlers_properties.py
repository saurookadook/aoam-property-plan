from __future__ import annotations

import pytest

from _factories.listing.db import ListingDBFactory
from _factories.market.db import MarketDBFactory
from api.routes.handlers.properties import (
    MARKET_MATCH_RADIUS_KM,
    resolve_market_id,
)

# Real positions, so the distances between them are the ones the roster actually
# has to tell apart.
SALENTO = (4.6375, -75.5703)
CALIMA = (3.9333, -76.4833)
PANCE = (3.3406, -76.5622)
CARTAGENA = (10.3910, -75.4794)


@pytest.fixture
def ingested_markets(test_db_session):
    """
    Three markets, each with one ingested listing, so each has a centroid sitting
    exactly on its reference point.
    """
    points = {"Salento": SALENTO, "Calima": CALIMA, "Pance": PANCE}

    markets = {locality: MarketDBFactory(locality=locality) for locality in points}
    # Committed before the listings: ``listings.market_id`` is a real foreign key
    # and the factories pass it as a plain value, so nothing tells the unit of
    # work to insert the markets first.
    test_db_session.commit()

    for locality, (latitude, longitude) in points.items():
        ListingDBFactory(
            market_id=markets[locality].id,
            latitude=latitude,
            longitude=longitude,
            location=f"POINT({longitude} {latitude})",
        )

    test_db_session.commit()
    return markets


class TestResolveMarketId:
    def test_files_a_property_under_the_nearest_market(
        self, ingested_markets, test_db_session
    ):
        latitude, longitude = SALENTO

        result = resolve_market_id(
            test_db_session, latitude=latitude + 0.01, longitude=longitude + 0.01
        )

        assert result == ingested_markets["Salento"].id

    def test_ignores_the_city_a_listing_page_claims(
        self, ingested_markets, test_db_session
    ):
        """
        The reason this resolves on coordinates at all: a Pance cabin is filed by
        Finca Raiz under ``city='Cali'``, and ``markets`` has no Cali row here to
        match that against. Only the position says Pance.
        """
        latitude, longitude = PANCE

        result = resolve_market_id(
            test_db_session, latitude=latitude, longitude=longitude
        )

        assert result == ingested_markets["Pance"].id

    def test_no_market_beyond_the_match_radius(self, ingested_markets, test_db_session):
        latitude, longitude = CARTAGENA

        # Cartagena is roughly 700km from the nearest of the three, so nearest
        # centroid on its own would still have filed it under one of them.
        assert (
            resolve_market_id(test_db_session, latitude=latitude, longitude=longitude)
            is None
        )

    def test_no_market_when_nothing_has_been_ingested(self, test_db_session):
        MarketDBFactory(locality="Salento")
        test_db_session.commit()

        latitude, longitude = SALENTO

        # A market with no listings has no centroid, so there is nothing to
        # measure against - the market existing is not enough.
        assert (
            resolve_market_id(test_db_session, latitude=latitude, longitude=longitude)
            is None
        )

    def test_picks_the_nearer_of_two_neighbouring_markets(
        self, ingested_markets, test_db_session
    ):
        """
        Calima and Pance are about 66km apart, so a point between them is inside
        both radii and the radius decides nothing. Nearest is what breaks the tie:
        the point below is 22km from Pance and 44km from Calima.
        """
        midpoint_latitude = (CALIMA[0] + PANCE[0]) / 2
        midpoint_longitude = (CALIMA[1] + PANCE[1]) / 2

        # Nudged towards Pance so the expected answer is not a coin flip.
        result = resolve_market_id(
            test_db_session,
            latitude=midpoint_latitude - 0.1,
            longitude=midpoint_longitude,
        )

        assert result == ingested_markets["Pance"].id

    def test_the_radius_is_wide_enough_for_a_markets_own_footprint(
        self, ingested_markets, test_db_session
    ):
        """
        A property on the edge of a market still matches. 0.2 degrees of latitude
        is roughly 22km - well inside ``MARKET_MATCH_RADIUS_KM`` and well inside
        the sprawl of a Colombian municipality.
        """
        latitude, longitude = SALENTO

        assert MARKET_MATCH_RADIUS_KM >= 25.0
        assert (
            resolve_market_id(
                test_db_session, latitude=latitude + 0.2, longitude=longitude
            )
            == ingested_markets["Salento"].id
        )
