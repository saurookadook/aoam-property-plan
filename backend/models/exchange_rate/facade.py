from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Optional, Union
from uuid import UUID

from sqlalchemy import select, update, or_
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import NoResultFound

from models.base.facade import BaseFacade
from models.exchange_rate.db import ExchangeRateDB
from models.exchange_rate.entity import ExchangeRateEntity


class ExchangeRateFacade(BaseFacade):
    class NoResultFound(Exception):
        pass

    def get_one_by_id(self, id: UUID | str) -> ExchangeRateEntity:
        try:
            exchange_rate = self.db_session.execute(
                select(ExchangeRateDB).where(ExchangeRateDB.id == id)
            ).scalar_one()
        except NoResultFound:
            raise ExchangeRateFacade.NoResultFound(
                f"Exchange rate record with ``id='{id}'`` not found"
            )
        return ExchangeRateEntity.model_validate(exchange_rate)

    def get_one_by_date(self, record_date: date | str) -> ExchangeRateEntity:
        try:
            exchange_rate = self.db_session.execute(
                select(ExchangeRateDB).where(ExchangeRateDB.record_date == record_date)
            ).scalar_one()
        except NoResultFound:
            raise ExchangeRateFacade.NoResultFound(
                f"Exchange rate record with ``date='{record_date}'`` not found"
            )
        return ExchangeRateEntity.model_validate(exchange_rate)

    def create_or_update(self, *, payload: dict) -> ExchangeRateEntity:
        maybe_one = self._find_one_if_exists(
            id=payload.get("id"), record_date=payload.get("record_date")
        )
        if maybe_one:
            return self.update(payload=payload)

        insert_stmt = insert(ExchangeRateDB).values(**payload)

        full_stmt = insert_stmt.on_conflict_do_update(
            constraint=ExchangeRateDB.__table__.primary_key,
            set_={
                **payload,
                "updated_at": datetime.now(timezone.utc),
            },
        ).returning(ExchangeRateDB)

        exchange_rate_record = self.db_session.execute(full_stmt).scalar_one()
        self.db_session.flush()

        return ExchangeRateEntity.model_validate(exchange_rate_record)

    def update(self, *, payload: dict) -> ExchangeRateEntity:
        where_clause = (
            ExchangeRateDB.id == payload.get("id")
            if payload.get("id") is not None
            else ExchangeRateDB.record_date == payload.get("record_date")
        )
        update_stmt = (
            update(ExchangeRateDB).where(where_clause).values(**payload)
        ).returning(ExchangeRateDB)

        updated_record = self.db_session.execute(update_stmt).scalar_one()
        self.db_session.flush()

        return ExchangeRateEntity.model_validate(updated_record)

    def _find_one_if_exists(
        self,
        *,
        id: Optional[UUID | str] = None,
        record_date: Optional[date | str] = None,
    ) -> ExchangeRateEntity | None:
        try:
            if not id:
                raise ValueError("No 'id' provided to find exchange rate record")

            return self.get_one_by_id(id=id)
        except (ValueError, ExchangeRateFacade.NoResultFound):
            pass

        try:
            if not record_date:
                raise ValueError(
                    "No 'record_date' provided to find exchange rate record"
                )

            return self.get_one_by_date(record_date=record_date)
        except (ValueError, ExchangeRateFacade.NoResultFound):
            pass

        return None
