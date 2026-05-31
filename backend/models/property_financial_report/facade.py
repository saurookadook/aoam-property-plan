from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional, Union
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import NoResultFound

from models.base.facade import BaseFacade
from models.property_financial_report.db import PropertyFinancialReportDB
from models.property_financial_report.entity import (
    PropertyFinancialReportEntity,
)


class PropertyFinancialReportFacade(BaseFacade):
    class NoResultFound(Exception):
        pass

    def get_one_by_id(self, id: UUID | str) -> PropertyFinancialReportEntity:
        try:
            property_financial_report = self.db_session.execute(
                select(PropertyFinancialReportDB).where(
                    PropertyFinancialReportDB.id == id
                )
            ).scalar_one()
        except NoResultFound:
            raise PropertyFinancialReportFacade.NoResultFound(
                f"Property financial report record with ``id='{id}'`` not found"
            )
        return PropertyFinancialReportEntity.model_validate(property_financial_report)

    def create_or_update(self, *, payload: dict) -> PropertyFinancialReportEntity:
        maybe_one = self._find_one_if_exists(id=payload.get("id"))
        if maybe_one:
            return self.update(payload=payload)

        insert_stmt = insert(PropertyFinancialReportDB).values(**payload)

        full_stmt = insert_stmt.on_conflict_do_update(
            constraint=PropertyFinancialReportDB.__table__.primary_key,
            set_={
                **payload,
                "updated_at": datetime.now(timezone.utc),
            },
        ).returning(PropertyFinancialReportDB)

        property_financial_report_record = self.db_session.execute(
            full_stmt
        ).scalar_one()
        self.db_session.flush()

        return PropertyFinancialReportEntity.model_validate(
            property_financial_report_record
        )

    def update(self, *, payload: dict) -> PropertyFinancialReportEntity:
        update_stmt = (
            update(PropertyFinancialReportDB)
            .where(PropertyFinancialReportDB.id == payload.get("id"))
            .values(**payload)
        ).returning(PropertyFinancialReportDB)

        updated_record = self.db_session.execute(update_stmt).scalar_one()
        self.db_session.flush()

        return PropertyFinancialReportEntity.model_validate(updated_record)

    def _find_one_if_exists(
        self, *, id: Optional[Union[UUID, str]] = None
    ) -> PropertyFinancialReportEntity | None:
        try:
            if not id:
                raise ValueError(
                    "No 'id' provided to find property financial report record"
                )

            return self.get_one_by_id(id=id)
        except (ValueError, PropertyFinancialReportFacade.NoResultFound):
            pass

        return None
