from __future__ import annotations

import re
from uuid import UUID, uuid4

from pydantic import alias_generators
from sqlalchemy import MetaData
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import (
    Mapped,
    as_declarative,
    declared_attr,
    mapped_column,
    sessionmaker,
    scoped_session,
)
from sqlalchemy.types import TypeDecorator


@as_declarative()
class BaseDB:
    metadata: MetaData

    __table_args__ = {"extend_existing": True}

    @declared_attr
    def __tablename__(cls) -> str:
        # TODO: probably have to trim off the `_db` too...?
        db_suffix = re.compile(r"_db$", flags=re.IGNORECASE | re.MULTILINE)
        snakified_name = alias_generators.to_snake(cls.__class__.__name__)
        return re.sub(db_suffix, "", snakified_name)

    id: Mapped[UUID] = mapped_column(
        postgresql.UUID(as_uuid=True), primary_key=True, default=uuid4
    )


BaseDB.metadata.naming_convention = {
    "ix": "ix_%(column_0_N_label)s",
    "uq": "%(table_name)s_%(column_0_N_name)s_key",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "%(table_name)s_%(column_0_N_name)s_fkey",
    "pk": "%(table_name)s_pkey",
}
