# pyright: reportIncompatibleVariableOverride=false
from __future__ import annotations

from datetime import timedelta
from uuid import uuid4

import factory

from _factories.base_meta import BaseMetaFactory
from _factories.mixins.entity import TimestampsEntityFactoryMixin
from models.market_financial_report.entity import MarketFinancialReportEntity


class MarketFinancialReportEntityFactory(
    TimestampsEntityFactoryMixin,
    factory.Factory,
    metaclass=BaseMetaFactory[MarketFinancialReportEntity],
):
    class Meta:
        model = MarketFinancialReportEntity

    id = factory.LazyFunction(uuid4)
    market_id = factory.LazyFunction(
        uuid4
    )  # NOTE: this should probably just throw if it's not provided?
    country = factory.Faker("country")
    adr_cop = factory.Faker("pyfloat", positive=True, min_value=50, max_value=500)
    annual_revenue_cop = factory.Faker(
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
