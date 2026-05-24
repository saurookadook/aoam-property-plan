from __future__ import annotations

from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column

from db.base_db import BaseDB
from models.mixins import TimestampsDB


class ExchangeRateDB(BaseDB, TimestampsDB):
    record_date: Mapped[str] = mapped_column(
        postgresql.DATE, nullable=False, primary_key=True
    )
    cop_per_usd: Mapped[float] = mapped_column(postgresql.REAL, nullable=False)
