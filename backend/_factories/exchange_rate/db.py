# pyright: reportIncompatibleVariableOverride=false
from __future__ import annotations

from datetime import timedelta
from random import randint

import factory

from _factories.base_meta import BaseMetaFactory
from _factories.mixins.db import TimestampsDBMixinFactory
from db.db_session_manager import DBSessionManager
from models.exchange_rate.db import ExchangeRateDB


class ExchangeRateDBFactory(
    TimestampsDBMixinFactory,
    factory.alchemy.SQLAlchemyModelFactory,
    metaclass=BaseMetaFactory[ExchangeRateDB],
):
    class Meta:
        model = ExchangeRateDB
        sqlalchemy_session = DBSessionManager().scoped_session

    record_date = factory.LazyAttribute(
        lambda o: o.created_at - timedelta(minutes=randint(0, 600))
    )
    cop_per_usd = factory.Faker(
        "pyfloat", positive=True, min_value=0.01, max_value=5000
    )
