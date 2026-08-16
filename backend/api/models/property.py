from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from pydantic import BaseModel, Field, model_validator
from typing_extensions import Self

from models.property.entity import PropertyEntity
from utils.pydantic_helpers import BaseResponseModel

# Supplying these describes a property well enough to store without scraping.
# They are exactly the ``NOT NULL`` columns on ``properties`` that are neither
# defaulted (``status``, ``amenities``, ``source_created_at``) nor always
# required (``source_url``).
MANUAL_FIELDS = (
    "address",
    "bedrooms",
    "city",
    "country",
    "latitude",
    "longitude",
    "neighborhood",
    "property_type",
    "state",
)

# Accepted only alongside a manual entry - when scraping, these come off the page.
MANUAL_OPTIONAL_FIELDS = (
    "postal_code",
    "purchase_price_cop",
    "source_created_at",
    "status",
)

# Valid on either path, so they take no part in deciding which one applies.
OVERRIDE_FIELDS = (
    "amenities",
    "description",
    "name",
    "notes",
)


class PropertyCreateRequest(BaseModel):
    """
    Accepts a property one of two ways, told apart by whether the manual field
    set is present:

    - ``source_url`` on its own -> the listing is fetched and scraped.
    - ``source_url`` plus every field in ``MANUAL_FIELDS`` -> the body is stored
        as given and nothing is fetched. This also covers listing sites we have no
        parser for.

    ``source_url`` is required either way: it is ``NOT NULL`` on ``properties``,
    and its unique constraint is what stops a re-submission creating a duplicate.

    ``OVERRIDE_FIELDS`` may accompany either path and beat anything scraped, which
    is why they are excluded from the all-or-nothing check below.
    """

    source_url: str = Field(min_length=1)

    # --- manual entry: all of these, or none of them
    address: Optional[str] = None
    bedrooms: Optional[int] = None
    city: Optional[str] = None
    country: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    neighborhood: Optional[str] = None
    property_type: Optional[str] = None
    state: Optional[str] = None

    # --- manual entry only
    postal_code: Optional[str] = None
    purchase_price_cop: Optional[float] = None
    source_created_at: Optional[datetime] = None
    status: Optional[str] = None

    # --- valid on either path
    amenities: Optional[list[str]] = None
    description: Optional[str] = None
    name: Optional[str] = None
    notes: Optional[str] = None

    @property
    def is_manual(self) -> bool:
        return all(getattr(self, field) is not None for field in MANUAL_FIELDS)

    @model_validator(mode="after")
    def validate_manual_fields(self) -> Self:
        provided = [
            field for field in MANUAL_FIELDS if getattr(self, field) is not None
        ]

        if provided and len(provided) != len(MANUAL_FIELDS):
            missing = sorted(set(MANUAL_FIELDS) - set(provided))
            raise ValueError(
                "Manual entry requires all of "
                f"[{', '.join(MANUAL_FIELDS)}] - missing [{', '.join(missing)}]. "
                "Omit them all to scrape 'source_url' instead."
            )

        if not provided:
            unusable = [
                field
                for field in MANUAL_OPTIONAL_FIELDS
                if getattr(self, field) is not None
            ]
            if unusable:
                raise ValueError(
                    f"[{', '.join(unusable)}] are only accepted with a full manual "
                    "entry - when scraping, they are read from the listing page."
                )

        return self

    def manual_payload(self) -> dict[str, Any]:
        """Builds a ``properties`` payload straight from the request body."""
        payload: dict[str, Any] = {
            field: getattr(self, field) for field in MANUAL_FIELDS
        }

        for field in MANUAL_OPTIONAL_FIELDS:
            value = getattr(self, field)
            if value is not None:
                payload[field] = value

        payload.setdefault("source_created_at", datetime.now(timezone.utc))
        payload.setdefault("status", "active")

        return payload

    def overrides(self) -> dict[str, Any]:
        """
        Explicitly supplied values that beat whatever the scraper produced.

        Tested against ``None`` rather than truthiness so that an explicit empty
        ``amenities`` list clears the scraped one instead of falling back to it.
        """
        return {
            field: getattr(self, field)
            for field in OVERRIDE_FIELDS
            if getattr(self, field) is not None
        }


class PropertyResponse(BaseResponseModel):
    data: PropertyEntity
