from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict

from utils.pydantic_helpers import BaseResponseModel


class ExchangeRateData(BaseModel):
    """
    The rate the UI converts with, and the day it is for.

    Deliberately narrower than ``ExchangeRateEntity``: the currency toggle needs
    the number and the date it was recorded, and nothing on the client has any
    use for the row's ``id`` or its ``created_at``/``updated_at``. ``record_date``
    is not optional here for the same reason the route 503s on a missing rate -
    a figure shown without saying when it was true is worse than no figure.

    A plain ``BaseModel`` rather than a ``BaseResponseModel``: response models
    camel-case their field names, and every other payload the API serves nests
    snake_case entities under ``data``. A lone camelCase body would make the
    client's exchange-rate type the only one that does not mirror the backend
    field-for-field.
    """

    model_config = ConfigDict(from_attributes=True)

    cop_per_usd: float
    record_date: date


class ExchangeRateResponse(BaseResponseModel):
    data: ExchangeRateData
