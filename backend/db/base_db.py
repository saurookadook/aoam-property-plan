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
)


def simple_pluralize(word: str) -> str:
    if word.endswith(("s", "x", "z", "ch", "sh")):
        return word + "es"
    elif word.endswith("y") and word[-2] not in "aeiou":
        return word[:-1] + "ies"
    else:
        return word + "s"


@as_declarative()
class BaseDB:
    metadata: MetaData

    __table_args__ = {"extend_existing": True}

    @declared_attr  # type: ignore
    def __tablename__(cls) -> str:
        # TODO: probably have to trim off the `_db` too...?
        db_suffix = re.compile(r"_db$", flags=re.IGNORECASE | re.MULTILINE)
        snakeified_db_name = alias_generators.to_snake(cls.__name__)  # type: ignore
        snakeified_name = re.sub(db_suffix, "", snakeified_db_name)
        return simple_pluralize(snakeified_name)

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
