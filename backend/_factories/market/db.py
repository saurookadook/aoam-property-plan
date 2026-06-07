# pyright: reportIncompatibleVariableOverride=false
from __future__ import annotations

from datetime import timedelta
from uuid import uuid4

import factory

from _factories.base_meta import BaseMetaFactory
from _factories.mixins.db import TimestampsDBMixinFactory
from db.db_session_manager import DBSessionManager
from models.market.db import MarketDB


class MarketDBFactory(
    TimestampsDBMixinFactory,
    factory.alchemy.SQLAlchemyModelFactory,
    metaclass=BaseMetaFactory[MarketDB],
):
    class Meta:
        model = MarketDB
        sqlalchemy_session = DBSessionManager().scoped_session

    id = factory.LazyFunction(uuid4)
    country = factory.Faker("country")
    district = factory.Faker("street_name")
    locality = factory.Faker("city")
    region = factory.Faker("state")
