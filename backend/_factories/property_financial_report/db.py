# pyright: reportIncompatibleVariableOverride=false
from __future__ import annotations

from datetime import timedelta, timezone
from uuid import uuid4

import factory

from _factories.mixins.db import TimestampsDBMixinFactory

# from _mocks.temporal import get_mock_utcnow
from db.db_session_manager import DBSessionManager
from models.property_financial_report.db import PropertyFinancialReportDB


class PropertyFinancialReportDBFactory(
    TimestampsDBMixinFactory, factory.alchemy.SQLAlchemyModelFactory
):
    class Meta:
        model = PropertyFinancialReportDB
        sqlalchemy_session = DBSessionManager().scoped_session

    id = factory.LazyFunction(uuid4)
    property_id = factory.LazyFunction(uuid4)
    annual_net_income_usd = factory.Faker(
        "pyfloat", positive=True, min_value=10000, max_value=100000000
    )
    annual_revenue_usd = factory.Faker(
        "pyfloat", positive=True, min_value=10000, max_value=100000000
    )
    calculated_at = factory.LazyAttribute(
        lambda o: (o.created_at - timedelta(days=1)).replace(tzinfo=timezone.utc)
    )
    cash_invested_usd = factory.Faker(
        "pyfloat", positive=True, min_value=1000000, max_value=100000000
    )
    coc_return_percentage = factory.Faker("pyfloat", min_value=0, max_value=100)
    down_payment_percentage = factory.Faker("pyfloat", min_value=0, max_value=100)
    exchange_rate = factory.Faker("pyfloat", min_value=0, max_value=100)
    interest_rate = factory.Faker("pyfloat", min_value=0, max_value=100)
    loan_term_years = factory.Faker("pyfloat", min_value=0, max_value=100)
    monthly_expenses_usd = factory.Faker("pyfloat", min_value=1000, max_value=10000)
    payback_years = factory.Faker("pyfloat", min_value=0, max_value=100)
