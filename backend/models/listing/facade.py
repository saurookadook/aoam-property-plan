from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Optional, Union
from uuid import UUID

from sqlalchemy import func, select, true, update, and_
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import aliased, selectinload

from models.base.facade import BaseFacade
from models.listing.db import ListingDB
from models.listing.entity import ListingEntity, NewestListingEntity
from models.listing_financial_report.db import ListingFinancialReportDB
from models.market.facade import MarketFacade

_LISTING_COLUMNS = (
    ListingDB.id,
    ListingDB.airroi_id,
    ListingDB.amenities,
    ListingDB.baths,
    ListingDB.beds,
    ListingDB.bedrooms,
    ListingDB.cover_photo_url,
    ListingDB.description,
    ListingDB.latitude,
    # TODO: cleaner way to handle this conversion?
    func.ST_AsText(ListingDB.location).label("location"),
    ListingDB.longitude,
    ListingDB.market_id,
    ListingDB.name,
    ListingDB.photo_urls,
    ListingDB.property_type,
    ListingDB.source_url,
    ListingDB.created_at,
    ListingDB.updated_at,
)


# Relationship fields on `ListingEntity` that don't map to a column on
# `ListingDB` and therefore must be stripped before building insert/update
# statements against the table directly.
_NON_COLUMN_ENTITY_FIELDS = ("listing_financial_reports",)

# What ``sort`` on ``GET /api/markets/{market_id}`` orders by. Both live on the
# listing's latest financial report rather than on ``listings`` itself, which is
# why sorting needs the lateral in ``_apply_market_listing_order``.
MARKET_LISTING_SORT_COLUMNS = {
    "revenue": "ttm_revenue",
    "occupancy": "ttm_occupancy_rate",
}


class ListingFacade(BaseFacade):
    class NoResultFound(Exception):
        pass

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(self.__class__.__name__)

    def get_one_by_id(
        self, id: UUID | str, *, include_financial_reports: bool = False
    ) -> ListingEntity:
        select_clause = self._build_select_clause(
            include_financial_reports=include_financial_reports
        )
        try:
            stmt = self.db_session.execute(select_clause.where(ListingDB.id == id))
            listing = (
                stmt.scalar_one()
                if include_financial_reports
                else stmt.mappings().one()
            )
        except NoResultFound:
            raise ListingFacade.NoResultFound(
                f"Listing record with ``id='{id}'`` not found"
            )

        return ListingEntity.model_validate(listing)

    def get_one_by_airroi_id(
        self, airroi_id: int, *, include_financial_reports: bool = False
    ) -> ListingEntity:
        select_clause = self._build_select_clause(
            include_financial_reports=include_financial_reports
        )
        try:
            stmt = self.db_session.execute(
                select_clause.where(ListingDB.airroi_id == airroi_id)
            )
            listing = (
                stmt.scalar_one()
                if include_financial_reports
                else stmt.mappings().one()
            )
        except NoResultFound:
            raise ListingFacade.NoResultFound(
                f"Listing record with ``airroi_id='{airroi_id}'`` not found"
            )

        return ListingEntity.model_validate(listing)

    def get_all(self) -> list[ListingEntity]:
        listing_records = (
            self.db_session.execute(
                self._build_select_clause().order_by(ListingDB.airroi_id.asc())
            )
            .mappings()
            .all()
        )

        return [
            ListingEntity.model_validate(listing_record)
            for listing_record in listing_records
        ]

    def get_all_by_market_id(
        self,
        market_id: UUID | str,
        *,
        bedrooms: Optional[int] = None,
        property_type: Optional[str] = None,
        sort: Optional[str] = None,
        limit: Optional[int] = None,
        include_financial_reports: bool = False,
    ) -> list[ListingEntity]:
        """
        A market's listings, optionally filtered, sorted and capped.

        Every argument is pushed into the query. Filtering a market's listings in
        Python after fetching all of them would make ``limit`` cosmetic - Bogota
        alone is thousands of rows - and would leave ``sort`` describing the page
        rather than the market.

        NOTE: this changes the order callers see. There was no ``ORDER BY`` here
        before, so the order was whatever Postgres happened to return; it is now
        ``airroi_id`` ascending by default. That is a deliberate behaviour
        change: ``limit`` is meaningless without a total order, since "the first
        fifty" is not a defined set otherwise.

        Args:
            bedrooms: exact match on ``listings.bedrooms``.
            property_type: exact match on ``listings.property_type``.
            sort: one of ``MARKET_LISTING_SORT_COLUMNS``; ``None`` keeps the
                default ``airroi_id`` order.
            limit: maximum rows to return.
            include_financial_reports: eager-loads each listing's reports. See
                the note in ``_build_select_clause`` about ``location``.

        Raises:
            ValueError: for an unrecognised ``sort``.
        """
        market = MarketFacade(db_session=self.db_session).get_one_by_id(market_id)

        select_clause = self._build_select_clause(
            include_financial_reports=include_financial_reports
        ).where(ListingDB.market_id == market.id)

        if bedrooms is not None:
            select_clause = select_clause.where(ListingDB.bedrooms == bedrooms)

        if property_type is not None:
            select_clause = select_clause.where(
                ListingDB.property_type == property_type
            )

        select_clause = self._apply_market_listing_order(select_clause, sort=sort)

        if limit is not None:
            select_clause = select_clause.limit(limit)

        result = self.db_session.execute(select_clause)
        listing_records = (
            result.scalars().unique().all()
            if include_financial_reports
            else result.mappings().all()
        )

        return [
            ListingEntity.model_validate(listing_record)
            for listing_record in listing_records
        ]

    def get_newest(self) -> list[NewestListingEntity]:
        listing_records = (
            self.db_session.execute(
                select(
                    ListingDB.created_at,
                    ListingDB.cover_photo_url,
                    ListingDB.id,
                    ListingDB.market_id,
                    ListingDB.name,
                    ListingDB.updated_at,
                )
                .where(
                    and_(
                        ListingDB.created_at.isnot(None),
                        ListingDB.market_id.isnot(None),
                        ListingDB.name.isnot(None),
                    )
                )
                .order_by(ListingDB.created_at.desc())
                .limit(5)
            )
            .mappings()
            .all()
        )

        return [
            NewestListingEntity.model_validate(listing_record)
            for listing_record in listing_records
        ]

    def create_or_update(self, *, payload: dict[str, Any]) -> ListingEntity:
        maybe_one = self._find_one_if_exists(
            id=payload.get("id"), airroi_id=payload.get("airroi_id")
        )

        if maybe_one:
            return self.update(
                payload={
                    **maybe_one.model_dump(exclude=set(_NON_COLUMN_ENTITY_FIELDS)),
                    **payload,
                }
            )

        payload = self._strip_non_column_fields(payload)
        insert_stmt = insert(ListingDB).values(**payload)

        full_stmt = insert_stmt.on_conflict_do_update(
            constraint=ListingDB.__table__.primary_key,
            set_={
                **payload,
                "updated_at": datetime.now(timezone.utc),
            },
        ).returning(ListingDB.airroi_id)

        airroi_id = self.db_session.execute(full_stmt).scalar_one()
        self.db_session.flush()

        if airroi_id is None:
            raise ValueError("Failed to retrieve 'airroi_id' after insert/update")

        # TODO: this seems inefficient...
        return self.get_one_by_airroi_id(airroi_id=airroi_id)

    def update(self, *, payload: dict[str, Any]) -> ListingEntity:
        payload = self._strip_non_column_fields(payload)
        update_stmt = (
            update(ListingDB)
            .where(
                and_(
                    ListingDB.id == payload.get("id"),
                    ListingDB.airroi_id == payload.get("airroi_id"),
                )
            )
            .values(**payload)
        ).returning(ListingDB.airroi_id)

        airroi_id = self.db_session.execute(update_stmt).scalar_one()
        self.db_session.flush()

        if airroi_id is None:
            raise ValueError("Failed to retrieve 'airroi_id' after update")

        # TODO: this seems inefficient...
        return self.get_one_by_airroi_id(airroi_id=airroi_id)

    def _build_select_clause(self, *, include_financial_reports: bool = False):
        """
        NOTE: ``include_financial_reports=True`` selects the ORM entity rather
        than the explicit column list, so ``location`` is no longer built by
        ``ST_AsText``. ``ListingEntity`` reconstructs the WKT from
        ``latitude``/``longitude`` instead, which can render a different string
        for the same listing than ``/api/listings/{id}`` does. Compare
        coordinates, not ``location``, across the two modes.

        The ``selectinload`` is what makes that mode usable in a list: without it
        a fifty-listing market issues one query for the listings and fifty more
        for their reports.
        """
        if include_financial_reports:
            return (
                select(ListingDB)
                .select_from(ListingDB)
                .options(selectinload(ListingDB.listing_financial_reports))
            )

        return select(*_LISTING_COLUMNS).select_from(ListingDB)

    def _apply_market_listing_order(self, select_clause, *, sort: Optional[str]):
        """
        Orders a market's listings, defaulting to ``airroi_id`` ascending.

        ``revenue`` and ``occupancy`` live on ``listing_financial_reports``,
        which holds potentially several rows per listing, so they are reached
        through a ``LATERAL ... LIMIT 1`` for the newest report rather than a
        plain join - which would return a listing once per report it has.

        Nulls sort last either way: a listing with no report yet is not the
        market's best performer, and ``airroi_id`` breaks ties so the order is
        total and ``limit`` means something.
        """
        if sort is None:
            return select_clause.order_by(ListingDB.airroi_id.asc())

        sort_column_name = MARKET_LISTING_SORT_COLUMNS.get(sort)

        if sort_column_name is None:
            raise ValueError(
                f"Unknown listing sort '{sort}' - expected one of "
                f"{sorted(MARKET_LISTING_SORT_COLUMNS)}"
            )

        latest_report = aliased(
            ListingFinancialReportDB,
            (
                select(ListingFinancialReportDB)
                .where(ListingFinancialReportDB.listing_id == ListingDB.id)
                .order_by(
                    ListingFinancialReportDB.created_at.desc(),
                    ListingFinancialReportDB.id.desc(),
                )
                .limit(1)
                .lateral("latest_listing_financial_report")
            ),
        )

        return (
            select_clause.outerjoin(latest_report, true())
            .order_by(getattr(latest_report, sort_column_name).desc().nullslast())
            .order_by(ListingDB.airroi_id.asc())
        )

    def _strip_non_column_fields(self, payload: dict[str, Any]) -> dict[str, Any]:
        return {
            key: value
            for key, value in payload.items()
            if key not in _NON_COLUMN_ENTITY_FIELDS
        }

    def _find_one_if_exists(
        self, *, id: Optional[Union[UUID, str]] = None, airroi_id: Optional[int] = None
    ) -> ListingEntity | None:
        try:
            if not airroi_id:
                self.logger.warning("No 'airroi_id' provided to find listing record")
                raise ValueError("No 'airroi_id' provided to find listing record")

            return self.get_one_by_airroi_id(airroi_id=airroi_id)
        except (ValueError, ListingFacade.NoResultFound):
            pass

        try:
            if not id:
                self.logger.warning("No 'id' provided to find listing record")
                return None

            return self.get_one_by_id(id=id)
        except (ValueError, ListingFacade.NoResultFound):
            pass

        return None
