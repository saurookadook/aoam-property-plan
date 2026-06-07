from __future__ import annotations

from datetime import datetime

from sqlalchemy import String
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column

from db.base_db import BaseDB
from models.mixins import TimestampsDB


class PropertyDB(BaseDB, TimestampsDB):
    address: Mapped[str] = mapped_column(postgresql.TEXT, nullable=False)
    bedrooms: Mapped[int] = mapped_column(postgresql.INTEGER, nullable=False)
    city: Mapped[str] = mapped_column(postgresql.TEXT, nullable=False)
    country: Mapped[str] = mapped_column(postgresql.TEXT, nullable=False)
    latitude: Mapped[float] = mapped_column(postgresql.REAL, nullable=False)
    longitude: Mapped[float] = mapped_column(postgresql.REAL, nullable=False)
    neighborhood: Mapped[str] = mapped_column(postgresql.TEXT, nullable=False)
    notes: Mapped[str] = mapped_column(String(), nullable=True)
    postal_code: Mapped[str] = mapped_column(postgresql.TEXT, nullable=False)
    property_type: Mapped[str] = mapped_column(postgresql.TEXT, nullable=False)
    purchase_price_cop: Mapped[float] = mapped_column(
        postgresql.NUMERIC, nullable=False
    )
    purchase_price_usd: Mapped[float] = mapped_column(postgresql.NUMERIC, nullable=True)
    source_created_at: Mapped[datetime] = mapped_column(
        postgresql.TIMESTAMP, nullable=False
    )
    source_url: Mapped[str] = mapped_column(postgresql.TEXT, nullable=False)
    state: Mapped[str] = mapped_column(postgresql.TEXT, nullable=False)
