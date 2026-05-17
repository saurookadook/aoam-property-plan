from __future__ import annotations

from datetime import datetime


class TimestampsEntityMixin:
    created_at: datetime
    updated_at: datetime
