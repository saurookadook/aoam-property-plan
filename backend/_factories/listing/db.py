# pyright: reportIncompatibleVariableOverride=false
from __future__ import annotations

from uuid import uuid4

import factory

from _factories.base_meta import BaseMetaFactory
from _factories.mixins.db import TimestampsDBMixinFactory
from db.db_session_manager import DBSessionManager
from models.listing.db import ListingDB

# from rich import inspect as ri


# def parse_value_from_point(point_str: str, index: int):
#     try:
#         point_str = point_str.strip()
#         if point_str.startswith("POINT(") and point_str.endswith(")"):
#             point_str = point_str[6:-1]
#             parts = point_str.split()
#             if len(parts) == 2:
#                 return float(parts[index])
#     except Exception as e:
#         raise ValueError(f"Invalid POINT string format: {point_str}") from e

#     raise ValueError(f"Invalid POINT string format: {point_str}")


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
    cover_photo_url = factory.Faker("url")
    latitude = factory.LazyAttribute(lambda obj: float(obj.location[0]))
    location = factory.Faker("location_on_land")
    longitude = factory.LazyAttribute(lambda obj: float(obj.location[1]))
    market_id = factory.LazyFunction(
        uuid4
    )  # NOTE: this should probably just throw if it's not provided?
    property_type = factory.Faker("word")
    source_url = factory.Faker("url")
