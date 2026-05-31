from __future__ import annotations

from datetime import date

from models.base.entity import BaseEntityModel
from models.mixins import TimestampsEntityMixin


class ExchangeRateEntity(BaseEntityModel, TimestampsEntityMixin):
    cop_per_usd: float
    record_date: date
