# pyright: reportIncompatibleVariableOverride=false
from __future__ import annotations

from uuid import uuid4

import factory

from _factories.mixins.db import TimestampsDBMixinFactory
from db.db_session_manager import DBSessionManager
from models.property.db import PropertyDB


class PropertyDBFactory(
    TimestampsDBMixinFactory, factory.alchemy.SQLAlchemyModelFactory
):
    class Meta:
        model = PropertyDB
        sqlalchemy_session = DBSessionManager().scoped_session

    id = factory.LazyFunction(uuid4)
    address = factory.Faker("address")
    bedrooms = factory.Faker("random_int", min=1, max=10)
    city = factory.Faker("city")
    country = factory.Faker("country")
    latitude = factory.Faker("latitude")
    longitude = factory.Faker("longitude")
    neighborhood = factory.Faker("street_name")
    postal_code = factory.Faker("postcode")
    property_type = factory.Faker("word")
    purchase_price_cop = factory.Faker(
        "pyfloat", positive=True, min_value=1000000, max_value=100000000
    )
    purchase_price_usd = factory.Faker(
        "pyfloat", positive=True, min_value=100000, max_value=1000000
    )
    source_url = factory.Faker("url")
    state = factory.Faker("state")
