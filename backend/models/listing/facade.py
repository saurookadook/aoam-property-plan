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
from models.listing.entity import ListingEntity


class ListingFacade(BaseFacade):
    class NoResultFound(Exception):
        pass

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(self.__class__.__name__)

    def get_one_by_id(self, id: UUID | str) -> ListingEntity:
        try:
            listing = (
                self.db_session.execute(
                    select(
                        ListingDB.id,
                        ListingDB.airroi_id,
                        ListingDB.bedrooms,
                        ListingDB.cover_photo_url,
                        ListingDB.latitude,
                        # TODO: cleaner way to handle this conversion?
                        func.ST_AsText(ListingDB.location).label("location"),
                        ListingDB.longitude,
                        ListingDB.market_id,
                        ListingDB.property_type,
                        ListingDB.source_url,
                        ListingDB.created_at,
                        ListingDB.updated_at,
                    ).where(ListingDB.id == id)
                )
                .mappings()
                .one()
            )
        except NoResultFound:
            raise ListingFacade.NoResultFound(
                f"Listing record with ``id='{id}'`` not found"
            )

        return ListingEntity.model_validate(listing)

    def get_one_by_airroi_id(self, airroi_id: int) -> ListingEntity:
        try:
            listing = (
                self.db_session.execute(
                    select(
                        ListingDB.id,
                        ListingDB.airroi_id,
                        ListingDB.bedrooms,
                        ListingDB.cover_photo_url,
                        ListingDB.latitude,
                        # TODO: cleaner way to handle this conversion?
                        func.ST_AsText(ListingDB.location).label("location"),
                        ListingDB.longitude,
                        ListingDB.market_id,
                        ListingDB.property_type,
                        ListingDB.source_url,
                        ListingDB.created_at,
                        ListingDB.updated_at,
                    ).where(ListingDB.airroi_id == airroi_id)
                )
                .mappings()
                .one()
            )
        except NoResultFound:
            raise ListingFacade.NoResultFound(
                f"Listing record with ``airroi_id='{airroi_id}'`` not found"
            )

        return ListingEntity.model_validate(listing)

    def create_or_update(self, *, payload: dict[str, Any]) -> ListingEntity:
        maybe_one = self._find_one_if_exists(
            id=payload.get("id"), airroi_id=payload.get("airroi_id")
        )

        if maybe_one:
            return self.update(payload={**maybe_one.model_dump(), **payload})

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

        # TODO: this seems inefficient...
        return self.get_one_by_airroi_id(airroi_id=airroi_id)

    def update(self, *, payload: dict[str, Any]) -> ListingEntity:
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

        # TODO: this seems inefficient...
        return self.get_one_by_airroi_id(airroi_id=airroi_id)

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
