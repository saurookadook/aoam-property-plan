# pyright: reportIncompatibleVariableOverride=false
from __future__ import annotations

from uuid import uuid4

import factory

from _factories.base_meta import BaseMetaFactory
from _factories.mixins.entity import TimestampsEntityFactoryMixin
from models.listing.entity import ListingEntity


class ListingEntityFactory(
    TimestampsEntityFactoryMixin,
    factory.Factory,
    metaclass=BaseMetaFactory[ListingEntity],
):
    class Meta:
        model = ListingEntity

    id = factory.LazyFunction(uuid4)
    airroi_id = factory.Sequence(lambda n: n + 1)
    bedrooms = factory.Sequence(lambda n: (n % 10) + 1)
    cover_photo_url = factory.Faker("url")
    latitude = factory.Faker("latitude")
    location = factory.Faker(
        "latlng"
    )  # NOTE: should maybe use `location_on_land` and then set lat/lng in `post_generation` method?
    longitude = factory.Faker("longitude")
    market_id = factory.LazyFunction(
        uuid4
    )  # NOTE: this should probably just throw if it's not provided?
    property_type = factory.Faker("word")
    source_url = factory.Faker("url")
