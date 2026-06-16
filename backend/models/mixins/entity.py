from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class TimestampsEntityMixin(BaseModel):
    created_at: datetime
    updated_at: datetime
