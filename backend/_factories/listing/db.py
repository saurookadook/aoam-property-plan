# pyright: reportIncompatibleVariableOverride=false
from __future__ import annotations

from uuid import uuid4

import factory

from _factories.base_meta import BaseMetaFactory
from _factories.mixins.db import TimestampsDBMixinFactory
from db.db_session_manager import DBSessionManager
from models.listing.db import ListingDB


class ListingDBFactory(
    TimestampsDBMixinFactory,
    factory.alchemy.SQLAlchemyModelFactory,
    metaclass=BaseMetaFactory[ListingDB],
):
    class Meta:
        model = ListingDB
        sqlalchemy_session = DBSessionManager().scoped_session

    id = factory.LazyFunction(uuid4)
    airroi_id = factory.Sequence(lambda n: n + 1)
    """
    Auto-incrementing integer starting from 1
    """

    bedrooms = factory.Faker("random_int", min=1, max=10)
    latitude = factory.Faker("latitude")
    location = factory.Faker("latlng")
    longitude = factory.Faker("longitude")
    market_id = factory.LazyFunction(uuid4)
    property_type = factory.Faker("word")
    source_url = factory.Faker("url")
