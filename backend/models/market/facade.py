from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional, Union
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import NoResultFound

from models.base.facade import BaseFacade
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
