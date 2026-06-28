from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional, Union
from uuid import UUID

from sqlalchemy import Date, and_, exists, func, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import NoResultFound

from models.base.facade import BaseFacade
from models.listing_financial_report.db import ListingFinancialReportDB
from models.listing_financial_report.entity import ListingFinancialReportEntity


class ListingFinancialReportFacade(BaseFacade):
    class NoResultFound(Exception):
        pass

    def get_one_by_id(self, id: UUID | str) -> ListingFinancialReportEntity:
        try:
            listing_financial_report = self.db_session.execute(
                select(ListingFinancialReportDB).where(
                    ListingFinancialReportDB.id == id
                )
            ).scalar_one()
        except NoResultFound:
            raise ListingFinancialReportFacade.NoResultFound(
                f"Listing financial report record with ``id='{id}'`` not found"
            )

        return ListingFinancialReportEntity.model_validate(listing_financial_report)

    def get_all_by_listing_id(
        self, listing_id: UUID | str
    ) -> list[ListingFinancialReportEntity]:
        try:
            listing_financial_reports = (
                self.db_session.execute(
                    select(ListingFinancialReportDB).where(
                        ListingFinancialReportDB.listing_id == listing_id
                    )
                )
                .scalars()
                .all()
            )
        except NoResultFound:
            raise ListingFinancialReportFacade.NoResultFound(
                f"Listing financial report record with ``listing_id='{listing_id}'`` not found"
            )

        return [
            ListingFinancialReportEntity.model_validate(record)
            for record in listing_financial_reports
        ]

    def has_one_by_listing_id_for_date(
        self, *, listing_id: UUID | str, target_date_str: str
    ) -> bool:
        target_date = datetime.strptime(target_date_str, "%Y-%m-%d").date()
        stmt = select(
            exists().where(
                and_(
                    ListingFinancialReportDB.listing_id == listing_id,
                    func.cast(ListingFinancialReportDB.created_at, Date) == target_date,
                )
            )
        )

        return bool(self.db_session.execute(stmt).scalar())

    def create_or_update(self, *, payload: dict) -> ListingFinancialReportEntity:
        maybe_one = self._find_one_if_exists(id=payload.get("id"))
        if maybe_one:
            return self.update(payload={**maybe_one.model_dump(), **payload})

        insert_stmt = insert(ListingFinancialReportDB).values(**payload)

        full_stmt = insert_stmt.on_conflict_do_update(
            constraint=ListingFinancialReportDB.__table__.primary_key,
            set_={
                **payload,
                "updated_at": datetime.now(timezone.utc),
            },
        ).returning(ListingFinancialReportDB)

        listing_financial_report_record = self.db_session.execute(
            full_stmt
        ).scalar_one()
        self.db_session.flush()

        return ListingFinancialReportEntity.model_validate(
            listing_financial_report_record
        )

    def update(self, *, payload: dict) -> ListingFinancialReportEntity:
        update_stmt = (
            update(ListingFinancialReportDB)
            .where(ListingFinancialReportDB.id == payload.get("id"))
            .values(**payload)
        ).returning(ListingFinancialReportDB)

        updated_record = self.db_session.execute(update_stmt).scalar_one()
        self.db_session.flush()

        return ListingFinancialReportEntity.model_validate(updated_record)

    def _find_one_if_exists(
        self,
        *,
        id: Optional[Union[UUID, str]] = None,
        # listing_id: Optional[Union[UUID, str]] = None,
    ) -> ListingFinancialReportEntity | None:
        # try:
        #     if not listing_id:
        #         raise ValueError(
        #             "No 'listing_id' provided to find listing financial report record"
        #         )

        #     return self.get_one_by_listing_id(listing_id=listing_id)
        # except (ValueError, ListingFinancialReportFacade.NoResultFound):
        #     pass

        try:
            if not id:
                raise ValueError(
                    "No 'id' provided to find listing financial report record"
                )

            return self.get_one_by_id(id=id)
        except (ValueError, ListingFinancialReportFacade.NoResultFound):
            pass

        return None
