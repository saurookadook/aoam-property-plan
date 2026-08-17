from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional, Union
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import NoResultFound

from models.base.facade import BaseFacade
from models.market.facade import MarketFacade
from models.market_financial_report.db import MarketFinancialReportDB
from models.market_financial_report.entity import (
    MarketFinancialReportEntity,
)


class MarketFinancialReportFacade(BaseFacade):
    class NoResultFound(Exception):
        pass

    def get_one_by_id(self, id: UUID | str) -> MarketFinancialReportEntity:
        try:
            market_financial_report = self.db_session.execute(
                select(MarketFinancialReportDB).where(MarketFinancialReportDB.id == id)
            ).scalar_one()
        except NoResultFound:
            raise MarketFinancialReportFacade.NoResultFound(
                f"Market financial report record with ``id='{id}'`` not found"
            )
        return MarketFinancialReportEntity.model_validate(market_financial_report)

    def get_all_by_market_id(
        self, market_id: UUID | str
    ) -> list[MarketFinancialReportEntity]:
        market = MarketFacade(db_session=self.db_session).get_one_by_id(market_id)

        mfr_records = (
            self.db_session.execute(
                select(MarketFinancialReportDB).where(
                    MarketFinancialReportDB.market_id == market.id
                )
            )
            .scalars()
            .all()
        )

        return [
            MarketFinancialReportEntity.model_validate(mfr_rec)
            for mfr_rec in mfr_records
        ]

    def get_latest_by_market_id(
        self, market_id: UUID | str
    ) -> Optional[MarketFinancialReportEntity]:
        """
        Returns the most recently reported figures for a market, or ``None`` when
        the market has never been summarised.

        NOTE: unlike the ``get_one_by_*`` methods, this does not raise - callers
        are expected to branch on a missing report.

        ``handle_markets_summaries`` inserts a fresh row on every run rather than
        updating one, so a market accumulates a history and "the report" has to
        mean the latest of them. Ordered on ``last_updated`` - AirROI's own
        timestamp for the figures, and the column that carries an index - with
        ``created_at`` breaking ties so the ordering is total.
        """
        market_financial_report = self.db_session.execute(
            select(MarketFinancialReportDB)
            .where(MarketFinancialReportDB.market_id == market_id)
            .order_by(
                MarketFinancialReportDB.last_updated.desc(),
                MarketFinancialReportDB.created_at.desc(),
            )
            .limit(1)
        ).scalar_one_or_none()

        if market_financial_report is None:
            return None

        return MarketFinancialReportEntity.model_validate(market_financial_report)

    def create_or_update(self, *, payload: dict) -> MarketFinancialReportEntity:
        maybe_one = self._find_one_if_exists(id=payload.get("id"))
        if maybe_one:
            return self.update(payload=payload)

        insert_stmt = insert(MarketFinancialReportDB).values(**payload)

        full_stmt = insert_stmt.on_conflict_do_update(
            constraint=MarketFinancialReportDB.__table__.primary_key,
            set_={
                **payload,
                "updated_at": datetime.now(timezone.utc),
            },
        ).returning(MarketFinancialReportDB)

        market_financial_report_record = self.db_session.execute(full_stmt).scalar_one()
        self.db_session.flush()

        return MarketFinancialReportEntity.model_validate(
            market_financial_report_record
        )

    def update(self, *, payload: dict) -> MarketFinancialReportEntity:
        update_stmt = (
            update(MarketFinancialReportDB)
            .where(MarketFinancialReportDB.id == payload.get("id"))
            .values(**payload)
        ).returning(MarketFinancialReportDB)

        updated_record = self.db_session.execute(update_stmt).scalar_one()
        self.db_session.flush()

        return MarketFinancialReportEntity.model_validate(updated_record)

    def _find_one_if_exists(
        self, *, id: Optional[Union[UUID, str]] = None
    ) -> MarketFinancialReportEntity | None:
        try:
            if not id:
                raise ValueError(
                    "No 'id' provided to find market financial report record"
                )

            return self.get_one_by_id(id=id)
        except (ValueError, MarketFinancialReportFacade.NoResultFound):
            pass

        return None
