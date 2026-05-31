from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, scoped_session
from sqlalchemy.exc import NoResultFound

from db.db_session_manager import DBSessionManager
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
