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

    amenities = factory.List(
        [
            factory.Faker("word"),
            factory.Faker("word"),
            factory.Faker("word"),
        ]
    )
    baths = factory.Faker("random_int", min=1, max=5)
    beds = factory.Faker("random_int", min=1, max=10)
    bedrooms = factory.Faker("random_int", min=1, max=10)
    cover_photo_url = factory.Faker("url")
    description = factory.Faker("text")
    latitude = factory.LazyAttribute(lambda obj: float(obj.location[0]))
    location = factory.Faker("location_on_land")
    longitude = factory.LazyAttribute(lambda obj: float(obj.location[1]))
    market_id = factory.LazyFunction(
        uuid4
    )  # NOTE: this should probably just throw if it's not provided?
    name = factory.Faker("sentence", nb_words=3)
    photo_urls = factory.List(
        [
            factory.Faker("url"),
            factory.Faker("url"),
        ]
    )
    property_type = factory.Faker("word")
    source_url = factory.Faker("url")
