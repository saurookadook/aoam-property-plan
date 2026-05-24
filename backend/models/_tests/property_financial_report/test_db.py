from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID

import factory
import pytest
from sqlalchemy import select, and_

from _factories.property.db import PropertyDBFactory
from _factories.property_financial_report.db import PropertyFinancialReportDBFactory
from models.property_financial_report.db import PropertyFinancialReportDB


@pytest.fixture
def test_property_record(test_db_session):
    property_record = PropertyDBFactory()
    test_db_session.commit()
    return property_record


@pytest.fixture
def expected_property_financial_report_dict(test_property_record, mock_utcnow):
    calculated_at = (
        (mock_utcnow - timedelta(days=5)).replace(tzinfo=timezone.utc).isoformat()
    )

    return dict(
        id=UUID("53cd9d19-65f7-4796-ac2c-b6616eb46d63"),
        property_id=test_property_record.id,
        annual_net_income_usd=50000.0,
        annual_revenue_usd=20000.0,
        calculated_at=calculated_at,
        cash_invested_usd=10000.0,
        coc_return_percentage=10.0,
        down_payment_percentage=20.0,
        exchange_rate=1.7,
        interest_rate=5.0,
        loan_term_years=30,
        monthly_expenses_usd=2000.0,
        payback_years=5.0,
    )


def test_property_financial_report_db(
    expected_property_financial_report_dict, mock_utcnow, test_db_session
):
    expected_dict = expected_property_financial_report_dict
    property_financial_report = PropertyFinancialReportDBFactory(**expected_dict)
    test_db_session.commit()

    result = test_db_session.execute(
        select(PropertyFinancialReportDB).where(
            and_(
                PropertyFinancialReportDB.id == expected_dict["id"],
                PropertyFinancialReportDB.property_id == expected_dict["property_id"],
            )
        )
    ).scalar_one()

    assert result.id == expected_dict["id"]
    assert result.property_id == expected_dict["property_id"]
    assert result.annual_net_income_usd == expected_dict["annual_net_income_usd"]
    assert result.annual_revenue_usd == expected_dict["annual_revenue_usd"]
    assert (
        result.calculated_at.replace(tzinfo=timezone.utc).isoformat()
        == expected_dict["calculated_at"]
    )
    assert result.cash_invested_usd == expected_dict["cash_invested_usd"]
    assert result.coc_return_percentage == expected_dict["coc_return_percentage"]
    assert result.down_payment_percentage == expected_dict["down_payment_percentage"]
    assert result.exchange_rate == expected_dict["exchange_rate"]
    assert result.interest_rate == expected_dict["interest_rate"]
    assert result.loan_term_years == expected_dict["loan_term_years"]
    assert result.monthly_expenses_usd == expected_dict["monthly_expenses_usd"]
    assert result.payback_years == expected_dict["payback_years"]
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
