from __future__ import annotations

from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column

from db.base_db import BaseDB
from models.mixins import TimestampsDB


class MarketDB(BaseDB, TimestampsDB):
    """
    From biggest to smallest:
    - country
    - region
    - locality
    - district
    """

    country: Mapped[str] = mapped_column(postgresql.TEXT, nullable=False)
    district: Mapped[str] = mapped_column(postgresql.TEXT, nullable=True)
    locality: Mapped[str] = mapped_column(postgresql.TEXT, nullable=False)
    region: Mapped[str] = mapped_column(postgresql.TEXT, nullable=False)
