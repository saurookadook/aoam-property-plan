from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, ConfigDict


class MarketCentroidEntity(BaseModel):
    """
    Where a market is, averaged out of the listings ingested for it.

    Deliberately not a row and not columns on ``markets``. ``markets`` holds four
    geographic strings and nothing else; a centroid is derived data that moves
    with every ``listings_by_market`` run, so persisting it would mean a value
    that is stale between ingests and a second writer to keep honest. It is
    computed in the read query instead - see ``MarketFacade.get_centroid_by_id``.

    Not a ``BaseEntityModel``: there is no ``markets_centroids`` table and so no
    ``id`` of its own. ``market_id`` is the identity.
    """

    model_config = ConfigDict(from_attributes=True)

    market_id: UUID
    latitude: float
    longitude: float
    listing_count: int
    """
    How many listings the average was taken over. Served alongside the point so a
    caller can tell a centroid backed by fifty listings from one backed by two,
    and is *not* ``market_financial_reports.listing_count`` - that is AirROI's
    count for the whole market, this is how much of it we have ingested.
    """
