from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional, Union
from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import NoResultFound

from models.base.facade import BaseFacade
from models.listing.db import ListingDB
from models.listing.entity import ListingEntity


class ListingFacade(BaseFacade):
    class NoResultFound(Exception):
        pass

    def get_one_by_id(self, id: UUID | str) -> ListingEntity:
        try:
            listing = (
                self.db_session.execute(
                    select(
                        ListingDB.id,
                        ListingDB.adr_cop,
                        ListingDB.adr_usd,
                        ListingDB.airroi_id,
                        ListingDB.annual_revenue_cop,
                        ListingDB.annual_revenue_usd,
                        ListingDB.bedrooms,
                        ListingDB.latitude,
                        # TODO: cleaner way to handle this conversion?
                        func.ST_AsText(ListingDB.location).label("location"),
                        ListingDB.longitude,
                        ListingDB.market_id,
                        ListingDB.occupancy_rate,
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

        return ListingEntity.model_validate(dict(listing))

    def create_or_update(self, *, payload: dict[str, Any]) -> ListingEntity:
        maybe_one = self._find_one_if_exists(id=payload.get("id"))
        if maybe_one:
            return self.update(payload=payload)

        insert_stmt = insert(ListingDB).values(**payload)

        full_stmt = insert_stmt.on_conflict_do_update(
            constraint=ListingDB.__table__.primary_key,
            set_={
                **payload,
                "updated_at": datetime.now(timezone.utc),
            },
        ).returning(ListingDB.id)

        listing_id = self.db_session.execute(full_stmt).scalar_one()
        self.db_session.flush()

        return self.get_one_by_id(id=listing_id)

    def update(self, *, payload: dict[str, Any]) -> ListingEntity:
        update_stmt = (
            update(ListingDB).where(ListingDB.id == payload.get("id")).values(**payload)
        ).returning(ListingDB.id)

        listing_id = self.db_session.execute(update_stmt).scalar_one()
        self.db_session.flush()

        return self.get_one_by_id(id=listing_id)

    def _find_one_if_exists(
        self, *, id: Optional[Union[UUID, str]] = None
    ) -> ListingEntity | None:
        try:
            if not id:
                raise ValueError("No 'id' provided to find listing record")

            return self.get_one_by_id(id=id)
        except (ValueError, ListingFacade.NoResultFound):
            pass

        return None
