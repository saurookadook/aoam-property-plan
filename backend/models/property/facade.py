from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional, Union
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import NoResultFound

from models.base.facade import BaseFacade
from models.property.db import PropertyDB
from models.property.entity import PropertyEntity


class PropertyFacade(BaseFacade):

    class NoResultFound(Exception):
        pass

    def get_one_by_id(self, id: UUID | str) -> PropertyEntity:
        try:
            property_record = self.db_session.execute(
                select(PropertyDB).where(PropertyDB.id == id)
            ).scalar_one()
        except NoResultFound:
            raise PropertyFacade.NoResultFound(
                f"Property record with ``id='{id}'`` not found"
            )
        return PropertyEntity.model_validate(property_record)

    def get_one_by_source_url(self, source_url: str) -> PropertyEntity:
        try:
            property_record = self.db_session.execute(
                select(PropertyDB).where(PropertyDB.source_url == source_url)
            ).scalar_one()
        except NoResultFound:
            raise PropertyFacade.NoResultFound(
                f"Property record with ``source_url='{source_url}'`` not found"
            )
        return PropertyEntity.model_validate(property_record)

    def create_or_update(self, *, payload: dict) -> PropertyEntity:
        maybe_one = self._find_one_if_exists(
            id=payload.get("id"), source_url=payload.get("source_url")
        )
        if maybe_one:
            return self.update(payload=payload)

        insert_stmt = insert(PropertyDB).values(**payload)

        full_stmt = insert_stmt.on_conflict_do_update(
            constraint=PropertyDB.__table__.primary_key,
            set_={
                **payload,
                "updated_at": datetime.now(timezone.utc),
            },
        ).returning(PropertyDB)

        property_record = self.db_session.execute(full_stmt).scalar_one()
        self.db_session.flush()

        return PropertyEntity.model_validate(property_record)

    def update(self, *, payload: dict) -> PropertyEntity:
        where_clause = (
            PropertyDB.id == payload.get("id")
            if payload.get("id") is not None
            else PropertyDB.source_url == payload.get("source_url")
        )
        update_stmt = (
            update(PropertyDB).where(where_clause).values(**payload)
        ).returning(PropertyDB)

        updated_record = self.db_session.execute(update_stmt).scalar_one()
        self.db_session.flush()

        return PropertyEntity.model_validate(updated_record)

    def _find_one_if_exists(
        self,
        *,
        id: Optional[Union[UUID, str]] = None,
        source_url: Optional[str] = None,
    ) -> PropertyEntity | None:
        try:
            if not id:
                raise ValueError("No 'id' provided to find property record")

            return self.get_one_by_id(id=id)
        except (ValueError, PropertyFacade.NoResultFound):
            pass

        try:
            if not source_url:
                raise ValueError("No 'source_url' provided to find property record")

            return self.get_one_by_source_url(source_url=source_url)
        except (ValueError, PropertyFacade.NoResultFound):
            pass

        return None
