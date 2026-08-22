from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional, Union
from uuid import UUID

from sqlalchemy import Select, func, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import NoResultFound

from models.base.facade import BaseFacade
from models.listing.db import ListingDB
from models.market.centroid import MarketCentroidEntity
from models.market.db import MarketDB
from models.market.entity import MarketEntity


class MarketFacade(BaseFacade):

    class NoResultFound(Exception):
        pass

    def get_one_by_id(self, id: UUID | str) -> MarketEntity:
        try:
            market = self.db_session.execute(
                select(MarketDB).where(MarketDB.id == id)
            ).scalar_one()
        except NoResultFound:
            raise MarketFacade.NoResultFound(
                f"Market record with ``id='{id}'`` not found"
            )
        return MarketEntity.model_validate(market)

    def get_all(self) -> list[MarketEntity]:
        """Gets all records in ``markets`` table.

        Returns:
            ``list[MarketEntity]``: A list of all market entities in the database,
                sorted by locality.
        """

        market_records = (
            self.db_session.execute(select(MarketDB).order_by(MarketDB.locality.asc()))
            .scalars()
            .all()
        )
        return [MarketEntity.model_validate(market) for market in market_records]

    def get_centroid_by_id(
        self, market_id: UUID | str
    ) -> Optional[MarketCentroidEntity]:
        """
        The average position of a market's ingested listings, or ``None`` when it
        has none.

        Averaged in Postgres rather than in Python so the map marker on
        ``/markets`` costs one row instead of every listing in the market -
        Bogota alone would be thousands. ``AVG`` over ``latitude``/``longitude``
        is the same rule ``api.crons.handlers._market_centroid`` applies, which
        is the point: the marker and the ``/calculator/estimate`` call that fills
        ``peak_months`` have to describe the same spot, or a market's seasonality
        is reported for somewhere it is not.

        A plain mean of degrees, which is wrong near the poles and across the
        antimeridian and irrelevantly so for a Colombian locality spanning a
        fraction of a degree.

        NOTE: does not raise for an unknown ``market_id`` - it returns ``None``,
        the same as a real market with nothing ingested yet. Callers branch on
        the absence either way.
        """
        # A ``GROUP BY`` over no matching rows yields no row at all rather than a
        # row of nulls, so "nothing ingested" and "no such market" both arrive
        # here as ``None``.
        centroid = self.db_session.execute(
            self._centroid_select().where(ListingDB.market_id == market_id)
        ).one_or_none()

        if centroid is None:
            return None

        return MarketCentroidEntity.model_validate(centroid)

    def get_all_centroids(self) -> list[MarketCentroidEntity]:
        """
        One centroid per market that has ingested listings, cheapest way to plot
        the whole roster.

        Markets with nothing ingested are absent rather than present with a null
        point: there is no position to report, and an entry that has to be
        null-checked by every caller is worse than no entry.
        """
        centroids = (
            self.db_session.execute(
                self._centroid_select()
                .where(ListingDB.market_id.isnot(None))
                .order_by(ListingDB.market_id)
            )
            .mappings()
            .all()
        )

        return [MarketCentroidEntity.model_validate(centroid) for centroid in centroids]

    def create_or_update(self, *, payload: dict) -> MarketEntity:
        maybe_one = self._find_one_if_exists(id=payload.get("id"))
        if maybe_one:
            return self.update(payload=payload)

        insert_stmt = insert(MarketDB).values(**payload)

        full_stmt = insert_stmt.on_conflict_do_update(
            constraint=MarketDB.__table__.primary_key,
            set_={
                **payload,
                # "created_at": arrow.utcnow(),
                "updated_at": datetime.now(timezone.utc),
            },
        ).returning(MarketDB)

        market_record = self.db_session.execute(full_stmt).scalar_one()
        self.db_session.flush()

        return MarketEntity.model_validate(market_record)

    def update(self, *, payload: dict) -> MarketEntity:
        update_stmt = (
            update(MarketDB).where(MarketDB.id == payload.get("id")).values(**payload)
        ).returning(MarketDB)

        updated_record = self.db_session.execute(update_stmt).scalar_one()
        self.db_session.flush()

        return MarketEntity.model_validate(updated_record)

    def _find_one_if_exists(
        self, *, id: Optional[Union[UUID, str]] = None
    ) -> MarketEntity | None:
        try:
            if not id:
                raise ValueError("No 'id' provided to find market record")

            return self.get_one_by_id(id=id)
        except (ValueError, MarketFacade.NoResultFound):
            pass

        return None

    def _centroid_select(self) -> Select:
        # ``latitude``/``longitude`` are ``NOT NULL`` on ``listings``, so the
        # ``AVG``s are null only when the group is empty - which for the grouped
        # form cannot happen, and for the single-market form is exactly the
        # "nothing ingested" case ``get_centroid_by_id`` checks for.
        return select(
            ListingDB.market_id.label("market_id"),
            func.avg(ListingDB.latitude).label("latitude"),
            func.avg(ListingDB.longitude).label("longitude"),
            func.count(ListingDB.id).label("listing_count"),
        ).group_by(ListingDB.market_id)
