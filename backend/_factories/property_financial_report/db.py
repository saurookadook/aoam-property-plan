# pyright: reportIncompatibleVariableOverride=false
from __future__ import annotations

from datetime import timedelta, timezone
from uuid import uuid4

import factory

from _factories.base_meta import BaseMetaFactory
from _factories.mixins.db import TimestampsDBMixinFactory
from db.db_session_manager import DBSessionManager
from models.property_financial_report.db import PropertyFinancialReportDB


class PropertyFinancialReportDBFactory(
    TimestampsDBMixinFactory,
    factory.alchemy.SQLAlchemyModelFactory,
    metaclass=BaseMetaFactory[PropertyFinancialReportDB],
):
    class Meta:
        model = PropertyFinancialReportDB
        sqlalchemy_session = DBSessionManager().scoped_session

    id = factory.LazyFunction(uuid4)
    property_id = factory.LazyFunction(uuid4)
    airroi_adr_cop = factory.Faker(
        "pyfloat", positive=True, min_value=179838.5, max_value=1798385
    )
    airroi_occupancy_rate = factory.Faker("pyfloat", min_value=0, max_value=1)
    airroi_revenue_cop = factory.Faker(
        "pyfloat", positive=True, min_value=359677000, max_value=35967700000
    )
    # Percentiles are generated as multiples of the mean rather than
    # independently, so a factory-built report keeps p25 < p50 < p75 < p90 the way
    # a real one does. The ratios are the salento 3br capture's.
    airroi_revenue_p25_cop = factory.LazyAttribute(
        lambda o: o.airroi_revenue_cop * 0.69
    )
    airroi_revenue_p50_cop = factory.LazyAttribute(
        lambda o: o.airroi_revenue_cop * 0.89
    )
    airroi_revenue_p75_cop = factory.LazyAttribute(
        lambda o: o.airroi_revenue_cop * 1.29
    )
    airroi_revenue_p90_cop = factory.LazyAttribute(
        lambda o: o.airroi_revenue_cop * 1.94
    )
    annual_net_income_cop = factory.Faker(
        "pyfloat", positive=True, min_value=359677000, max_value=359677000000
    )
    annual_net_income_usd = factory.Faker(
        "pyfloat", positive=True, min_value=1000, max_value=1000000
    )
    annual_revenue_cop = factory.Faker(
        "pyfloat", positive=True, min_value=359677000, max_value=359677000000
    )
    annual_revenue_source = "airroi_p25"
    annual_revenue_usd = factory.Faker(
        "pyfloat", positive=True, min_value=10000, max_value=1000000
    )
    assessed_value_cop = factory.Faker(
        "pyfloat", positive=True, min_value=35967700000, max_value=359677000000
    )
    calculated_at = factory.LazyAttribute(
        lambda o: (o.created_at - timedelta(days=1)).replace(tzinfo=timezone.utc)
    )
    cash_invested_cop = factory.Faker(
        "pyfloat", positive=True, min_value=35967700000, max_value=359677000000
    )
    cash_invested_usd = factory.Faker(
        "pyfloat", positive=True, min_value=100000, max_value=1000000
    )
    closing_costs_percentage = factory.Faker("pyfloat", min_value=0, max_value=10)
    coc_return_percentage = factory.Faker("pyfloat", min_value=0, max_value=100)
    # Above ``MIN_COMP_COUNT``, so a factory-built report is one whose
    # comp-derived estimate stood up rather than a thin-comp fallback.
    comp_count = factory.Faker("pyint", min_value=5, max_value=25)
    comp_derived_revenue_cop = factory.Faker(
        "pyfloat", positive=True, min_value=359677000, max_value=35967700000
    )
    down_payment_percentage = factory.Faker("pyfloat", min_value=0, max_value=100)
    exchange_rate = factory.Faker("pyfloat", min_value=0, max_value=100)
    hoa_monthly_cop = factory.Faker("pyfloat", min_value=0, max_value=1000000)
    interest_rate = factory.Faker("pyfloat", min_value=0, max_value=100)
    loan_term_years = factory.Faker("pyfloat", min_value=0, max_value=100)
    maintenance_reserve_percentage = factory.Faker("pyfloat", min_value=0, max_value=10)
    management_fee_percentage = factory.Faker("pyfloat", min_value=0, max_value=100)
    monthly_expenses_cop = factory.Faker(
        "pyfloat", min_value=35967700, max_value=3596770000
    )
    monthly_expenses_usd = factory.Faker("pyfloat", min_value=100, max_value=10000)
    monthly_mortgage_cop = factory.Faker(
        "pyfloat", min_value=35967700, max_value=3596770000
    )
    # Flat rather than random: the twelve shares have to sum to 1.0, and a
    # factory that quietly broke that invariant would make any seasonality
    # assertion meaningless.
    monthly_revenue_distribution = factory.List([1 / 12] * 12)
    payback_years = factory.Faker("pyfloat", min_value=0, max_value=100)
    peak_months = factory.List(["December", "July", "January"])
    predial_rate_percentage = factory.Faker("pyfloat", min_value=0, max_value=5)
    purchase_price_cop = factory.Faker(
        "pyfloat", positive=True, min_value=35967700000, max_value=359677000000
    )
    renovation_budget_cop = factory.Faker("pyfloat", min_value=0, max_value=100000000)
