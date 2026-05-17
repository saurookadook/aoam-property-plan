from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, ConfigDict, alias_generators


class BaseEntityModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID


class BaseResponseModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=alias_generators.to_camel,
        from_attributes=True,
        populate_by_name=True,
    )
