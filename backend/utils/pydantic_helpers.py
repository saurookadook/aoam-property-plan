from __future__ import annotations

from pydantic import BaseModel, ConfigDict, alias_generators


class BaseResponseModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=alias_generators.to_camel,
        from_attributes=True,
        populate_by_name=True,
    )
