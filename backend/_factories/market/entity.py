# pyright: reportIncompatibleVariableOverride=false
from __future__ import annotations

from uuid import uuid4

import factory

from _factories.base_meta import BaseMetaFactory
from _factories.mixins.entity import TimestampsEntityFactoryMixin
from models.market.entity import MarketEntity


class MarketEntityFactory(
    TimestampsEntityFactoryMixin,
    factory.Factory,
    metaclass=BaseMetaFactory[MarketEntity],
):
    class Meta:
        model = MarketEntity

    id = factory.LazyFunction(uuid4)
    country = factory.Faker("country")
    district = factory.Faker("street_name")
    locality = factory.Faker("city")
    region = factory.Faker("state")
