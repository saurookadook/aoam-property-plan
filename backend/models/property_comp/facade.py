from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional, Union
from uuid import UUID

from sqlalchemy import and_, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import NoResultFound

from models.base.facade import BaseFacade
from models.property_comp.db import PropertyCompDB
from models.property_comp.entity import PropertyCompEntity


class PropertyCompFacade(BaseFacade):
    class NoResultFound(Exception):
        pass

    def get_one_by_id(self, id: UUID | str) -> PropertyCompEntity:
        try:
            property_comp = self.db_session.execute(
                select(PropertyCompDB).where(PropertyCompDB.id == id)
            ).scalar_one()
        except NoResultFound:
            raise PropertyCompFacade.NoResultFound(
                f"Property comp record with ``id='{id}'`` not found"
            )
        return PropertyCompEntity.model_validate(property_comp)

    def get_one_by_property_id_and_listing_id(
        self, *, property_id: UUID | str, listing_id: UUID | str
    ) -> PropertyCompEntity:
        try:
            property_comp = self.db_session.execute(
                select(PropertyCompDB).where(
                    and_(
                        PropertyCompDB.property_id == property_id,
                        PropertyCompDB.listing_id == listing_id,
                    )
                )
            ).scalar_one()
        except NoResultFound:
            raise PropertyCompFacade.NoResultFound(
                f"Property comp record with ``property_id='{property_id}'`` and "
                f"``listing_id='{listing_id}'`` not found"
            )
        return PropertyCompEntity.model_validate(property_comp)

    def get_all_by_property_id(
        self, property_id: UUID | str
    ) -> list[PropertyCompEntity]:
        """
        Every comp held for a property, nearest first.

        Ordered by distance because that is the order the comps are read in -
        ``GET /api/properties/{id}/comps/cached`` shows them as a list of nearby
        properties. Comps AirROI returned without usable coordinates sort last
        rather than leading with a null.
        """
        property_comps = (
            self.db_session.execute(
                select(PropertyCompDB)
                .where(PropertyCompDB.property_id == property_id)
                .order_by(PropertyCompDB.distance_km.asc().nullslast())
            )
            .scalars()
            .all()
        )

        return [PropertyCompEntity.model_validate(record) for record in property_comps]

    def create_or_update(self, *, payload: dict) -> PropertyCompEntity:
        maybe_one = self._find_one_if_exists(
            id=payload.get("id"),
            property_id=payload.get("property_id"),
            listing_id=payload.get("listing_id"),
        )
        if maybe_one:
            # ``maybe_one.id`` beats the payload's, which is the whole point of
            # matching on the natural key: re-analysing a property hands us a
            # freshly minted ``id`` for a comp already on file, and updating on
            # that ``id`` would match no row at all.
            return self.update(payload={**payload, "id": maybe_one.id})

        insert_stmt = insert(PropertyCompDB).values(**payload)

        full_stmt = insert_stmt.on_conflict_do_update(
            constraint=PropertyCompDB.__table__.primary_key,
            set_={
                **payload,
                "updated_at": datetime.now(timezone.utc),
            },
        ).returning(PropertyCompDB)

        property_comp_record = self.db_session.execute(full_stmt).scalar_one()
        self.db_session.flush()

        return PropertyCompEntity.model_validate(property_comp_record)

    def update(self, *, payload: dict) -> PropertyCompEntity:
        where_clause = (
            PropertyCompDB.id == payload["id"]
            if payload.get("id") is not None
            else and_(
                PropertyCompDB.property_id == payload.get("property_id"),
                PropertyCompDB.listing_id == payload.get("listing_id"),
            )
        )
        update_stmt = (
            update(PropertyCompDB).where(where_clause).values(**payload)
        ).returning(PropertyCompDB)

        updated_record = self.db_session.execute(update_stmt).scalar_one()
        self.db_session.flush()

        return PropertyCompEntity.model_validate(updated_record)

    def _find_one_if_exists(
        self,
        *,
        id: Optional[Union[UUID, str]] = None,
        property_id: Optional[Union[UUID, str]] = None,
        listing_id: Optional[Union[UUID, str]] = None,
    ) -> PropertyCompEntity | None:
        try:
            if not id:
                raise ValueError("No 'id' provided to find property comp record")

            return self.get_one_by_id(id=id)
        except (ValueError, PropertyCompFacade.NoResultFound):
            pass

        # ``(property_id, listing_id)`` is the natural key, and re-analysing a
        # property mints a fresh ``id`` for a comp it has already seen. Without
        # this lookup that second run would insert past the primary-key conflict
        # clause and hit the unique constraint instead.
        try:
            if not property_id or not listing_id:
                raise ValueError(
                    "No 'property_id' and 'listing_id' pair provided to find "
                    "property comp record"
                )

            return self.get_one_by_property_id_and_listing_id(
                property_id=property_id, listing_id=listing_id
            )
        except (ValueError, PropertyCompFacade.NoResultFound):
            pass

        return None
