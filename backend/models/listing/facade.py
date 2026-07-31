from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Optional, Union
from uuid import UUID

from sqlalchemy import func, select, update, and_
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import NoResultFound

from models.base.facade import BaseFacade
from models.listing.db import ListingDB
from models.listing.entity import ListingEntity, NewestListingEntity
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

    def get_all_by_market_id(self, market_id: UUID | str) -> list[ListingEntity]:
        market = MarketFacade(db_session=self.db_session).get_one_by_id(market_id)

        listing_records = (
            self.db_session.execute(
                self._build_select_clause().where(ListingDB.market_id == market.id)
            )
            .mappings()
            .all()
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
        return (
            select(ListingDB)
            if include_financial_reports
            else select(*_LISTING_COLUMNS)
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
