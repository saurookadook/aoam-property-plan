# pyright: reportIncompatibleVariableOverride=false
from __future__ import annotations

from uuid import uuid4

import factory

from _factories.base_meta import BaseMetaFactory
from _factories.mixins.db import TimestampsDBMixinFactory
from db.db_session_manager import DBSessionManager
from models.listing_financial_report.db import ListingFinancialReportDB


class ListingFinancialReportDBFactory(
    TimestampsDBMixinFactory,
    factory.alchemy.SQLAlchemyModelFactory,
    metaclass=BaseMetaFactory[ListingFinancialReportDB],
):
    class Meta:
        model = ListingFinancialReportDB
        sqlalchemy_session = DBSessionManager().scoped_session

    id = factory.LazyFunction(uuid4)
    listing_id = factory.LazyFunction(uuid4)
    adr_cop = factory.Faker(
        "pyfloat", positive=True, min_value=179838.5, max_value=1798385
    )
    adr_usd = factory.Faker("pyfloat", positive=True, min_value=50, max_value=500)
    annual_revenue_cop = factory.Faker(
        "pyfloat", positive=True, min_value=359677000, max_value=35967700000
    )
    annual_revenue_usd = factory.Faker(
        "pyfloat", positive=True, min_value=1000, max_value=100000
    )
    occupancy_rate = factory.Faker("pyfloat", positive=True, min_value=0, max_value=1)
    # Ratings
    number_of_reviews = factory.Faker("pyint", min_value=0, max_value=100)
    rating_overall = factory.Faker("pyfloat", positive=True, min_value=0, max_value=5)
    rating_accuracy = factory.Faker("pyfloat", positive=True, min_value=0, max_value=5)
    rating_checkin = factory.Faker("pyfloat", positive=True, min_value=0, max_value=5)
    rating_cleanliness = factory.Faker(
        "pyfloat", positive=True, min_value=0, max_value=5
    )
    rating_communication = factory.Faker(
        "pyfloat", positive=True, min_value=0, max_value=5
    )
    rating_location = factory.Faker("pyfloat", positive=True, min_value=0, max_value=5)
    rating_value = factory.Faker("pyfloat", positive=True, min_value=0, max_value=5)
    # Performance Metrics
    ttm_revenue = factory.Faker(
        "pyfloat", positive=True, min_value=359677000, max_value=35967700000
    )
    ttm_avg_rate = factory.Faker(
        "pyfloat", positive=True, min_value=179838.5, max_value=1798385
    )
    ttm_occupancy_rate = factory.Faker(
        "pyfloat", positive=True, min_value=0, max_value=1
    )
    ttm_adjusted_occupancy_rate = factory.Faker(
        "pyfloat", positive=True, min_value=0, max_value=1
    )
    ttm_revpar = factory.Faker(
        "pyfloat", positive=True, min_value=179838.5, max_value=1798385
    )
    ttm_adjusted_revpar = factory.Faker(
        "pyfloat", positive=True, min_value=179838.5, max_value=1798385
    )
    ttm_total_days = factory.Faker("pyint", min_value=1, max_value=365)
    ttm_available_days = factory.Faker("pyint", min_value=1, max_value=365)
    ttm_blocked_days = factory.Faker("pyint", min_value=0, max_value=365)
    ttm_days_reserved = factory.Faker("pyint", min_value=0, max_value=365)
    ttm_avg_min_nights = factory.Faker(
        "pyfloat", positive=True, min_value=1, max_value=10
    )
    ttm_avg_length_of_stay = factory.Faker(
        "pyfloat", positive=True, min_value=1, max_value=30
    )
    l90d_revenue = factory.Faker(
        "pyfloat", positive=True, min_value=35967700, max_value=3596770000
    )
    l90d_avg_rate = factory.Faker(
        "pyfloat", positive=True, min_value=179838.5, max_value=1798385
    )
    l90d_occupancy_rate = factory.Faker(
        "pyfloat", positive=True, min_value=0, max_value=1
    )
    l90d_adjusted_occupancy_rate = factory.Faker(
        "pyfloat", positive=True, min_value=0, max_value=1
    )
    l90d_revpar = factory.Faker(
        "pyfloat", positive=True, min_value=179838.5, max_value=1798385
    )
    l90d_adjusted_revpar = factory.Faker(
        "pyfloat", positive=True, min_value=179838.5, max_value=1798385
    )
    l90d_total_days = factory.Faker("pyint", min_value=1, max_value=90)
    l90d_available_days = factory.Faker("pyint", min_value=1, max_value=90)
    l90d_blocked_days = factory.Faker("pyint", min_value=0, max_value=90)
    l90d_days_reserved = factory.Faker("pyint", min_value=0, max_value=90)
    l90d_avg_min_nights = factory.Faker(
        "pyfloat", positive=True, min_value=1, max_value=10
    )
    l90d_avg_length_of_stay = factory.Faker(
        "pyfloat", positive=True, min_value=1, max_value=30
    )
