from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column

from db.base_db import BaseDB
from models.mixins import TimestampsDB


class PropertyDB(BaseDB, TimestampsDB):
    address: Mapped[str] = mapped_column(postgresql.TEXT, nullable=False)
    amenities: Mapped[list[str]] = mapped_column(
        postgresql.ARRAY(postgresql.TEXT), nullable=False, server_default="{}"
    )
    baths: Mapped[Optional[float]] = mapped_column(postgresql.REAL, nullable=True)
    """
    ``REAL`` rather than ``INTEGER`` because half-baths are ubiquitous, mirroring
    ``ListingDB.baths`` so a property and a comp can be compared without a cast.
    """

    bedrooms: Mapped[int] = mapped_column(postgresql.INTEGER, nullable=False)
    city: Mapped[str] = mapped_column(postgresql.TEXT, nullable=False)
    country: Mapped[str] = mapped_column(postgresql.TEXT, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(postgresql.TEXT, nullable=True)
    guests: Mapped[Optional[int]] = mapped_column(postgresql.INTEGER, nullable=True)
    """
    Maximum occupancy. Finca Raiz does not publish it, so it is nullable and
    stands in as ``bedrooms x 2`` when AirROI needs it.
    """

    latitude: Mapped[float] = mapped_column(postgresql.REAL, nullable=False)
    longitude: Mapped[float] = mapped_column(postgresql.REAL, nullable=False)
    market_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("markets.id"), index=True, nullable=True
    )
    """
    Which market this property is being appraised against.

    Nullable, and resolved from ``latitude``/``longitude`` at create time rather
    than from ``city``/``state``: those come off the listing page as Finca Raiz
    wrote them, while ``markets.locality`` is AirROI's, and the two do not match
    - a Pance cabin is filed under ``city='Cali'``. A property that lands outside
    every market's listing footprint keeps a ``None`` here.
    """

    name: Mapped[Optional[str]] = mapped_column(postgresql.TEXT, nullable=True)
    neighborhood: Mapped[str] = mapped_column(postgresql.TEXT, nullable=False)
    notes: Mapped[str] = mapped_column(String(), nullable=True)
    postal_code: Mapped[Optional[str]] = mapped_column(postgresql.TEXT, nullable=True)
    property_type: Mapped[str] = mapped_column(postgresql.TEXT, nullable=False)
    purchase_price_cop: Mapped[Optional[float]] = mapped_column(
        postgresql.NUMERIC, nullable=True
    )
    purchase_price_usd: Mapped[float] = mapped_column(postgresql.NUMERIC, nullable=True)
    source_created_at: Mapped[datetime] = mapped_column(
        postgresql.TIMESTAMP, nullable=False
    )
    source_url: Mapped[str] = mapped_column(
        postgresql.TEXT, nullable=False, unique=True
    )
    state: Mapped[str] = mapped_column(postgresql.TEXT, nullable=False)
    status: Mapped[str] = mapped_column(
        postgresql.TEXT, nullable=False, server_default="'active'"
    )
