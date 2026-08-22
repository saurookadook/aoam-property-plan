from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from models.base.entity import BaseEntityModel
from models.listing.entity import CompListingEntity
from models.mixins import TimestampsEntityMixin


class PropertyCompEntity(BaseEntityModel, TimestampsEntityMixin):
    adr_cop: Optional[float] = None
    captured_at: datetime
    distance_km: Optional[float] = None
    listing_id: UUID
    occupancy_rate: Optional[float] = None
    property_id: UUID
    ttm_revenue_cop: Optional[float] = None
    ttm_total_days: Optional[float] = None


class PropertyCompWithListingEntity(PropertyCompEntity):
    """
    A comp row with the listing it froze its metrics from.

    Kept separate from ``PropertyCompEntity`` rather than widening it, following
    ``MarketWithFinancialReportEntity``. The write path validates one entity per
    comp inside ``_persist_comps`` with the relationship unloaded, and a field on
    the base class would make every one of those lazy-load a listing nothing
    asked for - and would put a relationship key into any payload built by
    round-tripping an entity through ``model_dump()``.

    ``listing`` is optional only so the two classes stay assignment-compatible;
    ``property_comps.listing_id`` is ``NOT NULL``, and the one facade method that
    returns this type eager-loads it.
    """

    listing: Optional[CompListingEntity] = None
