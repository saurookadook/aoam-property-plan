from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import and_, select

from _factories.listing.db import ListingDBFactory
from _factories.listing_financial_report.db import ListingFinancialReportDBFactory
from models.listing.db import ListingDB
from models.listing_financial_report.db import ListingFinancialReportDB


def test_listing_financial_report_db(
    expected_listing_dict,
    expected_listing_financial_report_dict,
    mock_utcnow,
    test_db_session,
):
    expected_dict = expected_listing_financial_report_dict

    ListingDBFactory(**expected_listing_dict)
    ListingFinancialReportDBFactory(**expected_dict)
    test_db_session.commit()

    result = test_db_session.execute(
        select(ListingFinancialReportDB)
        .join(ListingDB, ListingFinancialReportDB.listing_id == ListingDB.id)
        .where(
            and_(
                ListingFinancialReportDB.id == expected_dict["id"],
                ListingDB.id == expected_dict["listing_id"],
            )
        )
    ).scalar_one()

    assert result.id == expected_dict["id"]
    assert result.listing_id == expected_dict["listing_id"]
    assert result.adr_cop == expected_dict["adr_cop"]
    assert result.adr_usd == expected_dict["adr_usd"]
    assert result.annual_revenue_cop == expected_dict["annual_revenue_cop"]
    assert result.annual_revenue_usd == expected_dict["annual_revenue_usd"]
    assert result.occupancy_rate == expected_dict["occupancy_rate"]
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
