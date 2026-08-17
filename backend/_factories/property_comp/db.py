# pyright: reportIncompatibleVariableOverride=false
from __future__ import annotations

from uuid import uuid4

import factory

from _factories.base_meta import BaseMetaFactory
from _factories.mixins.db import TimestampsDBMixinFactory
from db.db_session_manager import DBSessionManager
from models.property_comp.db import PropertyCompDB


class PropertyCompDBFactory(
    TimestampsDBMixinFactory,
    factory.alchemy.SQLAlchemyModelFactory,
    metaclass=BaseMetaFactory[PropertyCompDB],
):
    class Meta:
        model = PropertyCompDB
        sqlalchemy_session = DBSessionManager().scoped_session

    id = factory.LazyFunction(uuid4)
    adr_cop = factory.Faker(
        "pyfloat", positive=True, min_value=179838.5, max_value=1798385
    )
    captured_at = factory.LazyAttribute(lambda o: o.created_at)
    # Not ``positive=True``: faker rejects that alongside a zero ``min_value``,
    # and a comp sitting on the property itself is a legitimate zero.
    distance_km = factory.Faker("pyfloat", min_value=0, max_value=50)
    listing_id = factory.LazyFunction(uuid4)
    occupancy_rate = factory.Faker("pyfloat", min_value=0, max_value=1)
    property_id = factory.LazyFunction(uuid4)
    ttm_revenue_cop = factory.Faker(
        "pyfloat", positive=True, min_value=359677000, max_value=35967700000
    )
    ttm_total_days = factory.Faker("pyint", min_value=1, max_value=365)
