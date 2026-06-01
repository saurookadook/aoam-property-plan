from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import and_, select

from _factories.market_financial_report.db import (
    MarketFinancialReportDBFactory,
)
from models.market_financial_report.db import MarketFinancialReportDB


def test_market_financial_report_db(
    expected_market_financial_report_dict, mock_utcnow, test_db_session
):
    expected_dict = expected_market_financial_report_dict
    MarketFinancialReportDBFactory(**expected_dict)
    test_db_session.commit()

    result = test_db_session.execute(
        select(MarketFinancialReportDB).where(
            and_(
                MarketFinancialReportDB.market_id == expected_dict["market_id"],
                MarketFinancialReportDB.last_updated == expected_dict["last_updated"],
            )
        )
    ).scalar_one()

    assert result.market_id == expected_dict["market_id"]
    assert result.adr_usd == expected_dict["adr_usd"]
    assert result.annual_revenue_usd == expected_dict["annual_revenue_usd"]
    expected_last_updated = datetime.fromisoformat(
        expected_dict["last_updated"]
    ).replace(tzinfo=timezone.utc)
    assert result.last_updated.replace(tzinfo=timezone.utc) == expected_last_updated
    assert result.listing_count == expected_dict["listing_count"]
    assert result.occupancy_rate == expected_dict["occupancy_rate"]
    assert result.peak_months == expected_dict["peak_months"]
    assert isinstance(result.created_at, datetime)
    assert isinstance(result.updated_at, datetime)
    assert (
        result.created_at.replace(tzinfo=timezone.utc).isoformat()
        == mock_utcnow.isoformat()
    )
    assert (
        result.updated_at.replace(tzinfo=timezone.utc).isoformat()
        == mock_utcnow.isoformat()
    )
