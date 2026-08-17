# pyright: reportIncompatibleVariableOverride=false
from __future__ import annotations

from datetime import timedelta, timezone
from uuid import uuid4

import factory

from _factories.base_meta import BaseMetaFactory
from _factories.mixins.db import TimestampsDBMixinFactory
from db.db_session_manager import DBSessionManager
from models.property.db import PropertyDB


class PropertyDBFactory(
    TimestampsDBMixinFactory,
    factory.alchemy.SQLAlchemyModelFactory,
    metaclass=BaseMetaFactory[PropertyDB],
):
    class Meta:
        model = PropertyDB
        sqlalchemy_session = DBSessionManager().scoped_session

    id = factory.LazyFunction(uuid4)
    address = factory.Faker("address")
    amenities = factory.List(
        [
            factory.Faker("word"),
            factory.Faker("word"),
            factory.Faker("word"),
        ]
    )
    baths = factory.Faker("pyfloat", positive=True, min_value=1, max_value=6)
    bedrooms = factory.Faker("random_int", min=1, max=10)
    city = factory.Faker("city")
    country = factory.Faker("country")
    description = factory.Faker("text")
    # The empirical median across the captured comps is roughly two guests per
    # bedroom, so a factory property lines up with what AirROI would be asked for.
    guests = factory.LazyAttribute(lambda o: o.bedrooms * 2)
    latitude = factory.Faker("latitude")
    longitude = factory.Faker("longitude")
    name = factory.Faker("sentence", nb_words=3)
    neighborhood = factory.Faker("street_name")
    postal_code = factory.Faker("postcode")
    property_type = factory.Faker("word")
    purchase_price_cop = factory.Faker(
        "pyfloat", positive=True, min_value=35967700000, max_value=359677000000
    )
    purchase_price_usd = factory.Faker(
        "pyfloat", positive=True, min_value=100000, max_value=1000000
    )
    source_created_at = factory.LazyAttribute(
        lambda o: (o.created_at - timedelta(days=5)).replace(tzinfo=timezone.utc)
    )
    source_url = factory.Faker("url")
    state = factory.Faker("state")
    status = "active"
