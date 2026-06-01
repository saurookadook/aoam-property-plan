# pyright: reportIncompatibleVariableOverride=false
from __future__ import annotations

from datetime import timedelta
from uuid import uuid4

import factory

from _factories.mixins.db import TimestampsDBMixinFactory
from db.db_session_manager import DBSessionManager
from models.market_financial_report.db import MarketFinancialReportDB


class MarketFinancialReportDBFactory(
    TimestampsDBMixinFactory, factory.alchemy.SQLAlchemyModelFactory
):
    class Meta:
        model = MarketFinancialReportDB
        sqlalchemy_session = DBSessionManager().scoped_session

    id = factory.LazyFunction(uuid4)
    market_id = factory.LazyFunction(uuid4)
    adr_usd = factory.Faker("pyfloat", positive=True, min_value=50, max_value=500)
    annual_revenue_usd = factory.Faker(
        "pyfloat", positive=True, min_value=1000, max_value=100000
    )
    last_updated = factory.LazyAttribute(lambda o: o.updated_at + timedelta(days=1))
    listing_count = factory.Faker("pyfloat", min_value=1.0, max_value=500.0)
    occupancy_rate = factory.Faker("pyfloat", positive=True, min_value=0.5, max_value=1)
    peak_months = factory.List(
        [
            factory.Faker("month_name"),
            factory.Faker("month_name"),
            factory.Faker("month_name"),
        ]
    )
