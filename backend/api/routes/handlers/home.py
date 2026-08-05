from __future__ import annotations

from collections import deque
from datetime import date, datetime, timezone
from uuid import UUID

from sqlalchemy import distinct, func, select, update, and_
from sqlalchemy.orm import Session

from models.market.db import MarketDB
from models.listing.db import ListingDB
from models.listing.entity import HighestEarningListingEntity
from models.listing_financial_report.db import ListingFinancialReportDB


def get_highest_earners(db_session: Session) -> list[HighestEarningListingEntity]:
    """
    Query:

    ```sql
    WITH results AS (
        SELECT DISTINCT ON (l.name) l.name, l.market_id, l.cover_photo_url, lfr.ttm_revenue
        FROM public.listings l
        JOIN public.listing_financial_reports lfr ON lfr.listing_id = l.id
        ORDER BY l.name
    )
    SELECT * FROM results r
    ORDER BY r.ttm_revenue DESC
    LIMIT 3;
    ```
    """

    subq = (
        select(
            distinct(ListingDB.name),
            ListingDB.created_at,
            ListingDB.cover_photo_url,
            ListingDB.id,
            ListingDB.market_id,
            ListingDB.name,
            ListingDB.updated_at,
            ListingFinancialReportDB.ttm_revenue,
        )
        .join(
            ListingFinancialReportDB,
            ListingFinancialReportDB.listing_id == ListingDB.id,
        )
        .order_by(ListingDB.name)
        .subquery()
    )

    results = (
        db_session.execute(
            select(
                subq.c.created_at,
                subq.c.cover_photo_url,
                subq.c.id,
                subq.c.market_id,
                subq.c.name,
                subq.c.updated_at,
                subq.c.ttm_revenue,
                MarketDB.country,
                MarketDB.locality,
                MarketDB.region,
            )
            .join(MarketDB, MarketDB.id == subq.c.market_id)
            .order_by(subq.c.ttm_revenue.desc())
            .limit(3)
        )
        .mappings()
        .all()
    )

return [HighestEarningListingEntity.model_validate(row) for row in results]
