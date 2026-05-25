from __future__ import annotations

from sqlalchemy import Column
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import func


class TimestampsDB(object):
    created_at = Column(
        postgresql.TIMESTAMP,
        server_default=func.now(),
        nullable=False,
    )
    updated_at = Column(
        postgresql.TIMESTAMP,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
