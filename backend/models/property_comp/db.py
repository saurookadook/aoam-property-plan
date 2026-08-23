from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base_db import BaseDB
from models.listing.db import ListingDB
from models.mixins import TimestampsDB


class PropertyCompDB(BaseDB, TimestampsDB):
    """
    A listing AirROI returned as a comparable for a property, with the metrics
    that comparison was made on frozen at the moment it was made.

    The join carries its own copy of ``adr_cop`` / ``occupancy_rate`` /
    ``ttm_revenue_cop`` / ``ttm_total_days`` rather than reading them back off
    ``listing_financial_reports``: those rows are overwritten by the nightly
    ingest, so a report re-read a week later would otherwise be explained by
    numbers that no longer produce it.
    """

    adr_cop: Mapped[Optional[float]] = mapped_column(postgresql.NUMERIC, nullable=True)
    captured_at: Mapped[datetime] = mapped_column(
        postgresql.TIMESTAMP(timezone=True), nullable=False
    )
    distance_km: Mapped[Optional[float]] = mapped_column(postgresql.REAL, nullable=True)
    """
    Haversine distance from the property, computed in Python at write time -
    AirROI returns coordinates on a comp but never a distance.
    """

    listing_id: Mapped[UUID] = mapped_column(ForeignKey("listings.id"), nullable=False)
    listing: Mapped[ListingDB] = relationship()
    """
    The listing this row froze its metrics from.

    No ``back_populates``: a listing is a comp of whatever properties happen to
    be near it, and nothing needs to ask a listing that question. Deliberately
    left lazy - only ``get_all_by_property_id`` eager-loads it, because that is
    the one read that renders a comp table.
    """

    occupancy_rate: Mapped[Optional[float]] = mapped_column(
        postgresql.REAL, nullable=True
    )
    property_id: Mapped[UUID] = mapped_column(
        ForeignKey("properties.id"), nullable=False
    )
    ttm_revenue_cop: Mapped[Optional[float]] = mapped_column(
        postgresql.NUMERIC, nullable=True
    )
    ttm_total_days: Mapped[Optional[float]] = mapped_column(
        postgresql.REAL, nullable=True
    )
    """
    Data-quality gate, not a multiplier: a comp whose ``adr x occupancy x
    ttm_total_days`` strays from its ``ttm_revenue_cop`` is dropped from the
    comp-derived estimate.
    """

    __table_args__ = (UniqueConstraint("property_id", "listing_id"),)
