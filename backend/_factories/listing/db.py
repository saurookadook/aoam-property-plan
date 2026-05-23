# pyright: reportIncompatibleVariableOverride=false
from __future__ import annotations

from datetime import timedelta
from uuid import uuid4

import factory

from _factories.mixins.db import TimestampsDBMixinFactory
from db.db_session_manager import DBSessionManager
from models.listing.db import ListingDB


class ListingDBFactory(
    TimestampsDBMixinFactory, factory.alchemy.SQLAlchemyModelFactory
):
    class Meta:
        model = ListingDB
        sqlalchemy_session = DBSessionManager().ScopedSession

    id = factory.LazyFunction(uuid4)
    adr_usd = factory.Faker("pyfloat", positive=True, min_value=50, max_value=500)
    airroi_id = factory.LazyFunction(uuid4)
    annual_revenue_usd = factory.Faker(
        "pyfloat", positive=True, min_value=1000, max_value=100000
    )
    bedrooms = factory.Faker("random_int", min=1, max=10)
    latitude = factory.Faker("latitude")
    location = factory.Faker("latlng")
    longitude = factory.Faker("longitude")
    market_id = factory.LazyFunction(uuid4)
    occupancy_rate = factory.Faker("pyfloat", positive=True, min_value=0, max_value=1)
    property_type = factory.Faker("word")
    source_url = factory.Faker("url")
