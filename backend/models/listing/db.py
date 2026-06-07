from __future__ import annotations

from uuid import UUID

from geoalchemy2 import Geography, WKBElement
from sqlalchemy import ForeignKey, Index
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column

from db.base_db import BaseDB
from models.mixins import TimestampsDB


class ListingDB(BaseDB, TimestampsDB):
    airroi_id: Mapped[int] = mapped_column(
        postgresql.BIGINT, nullable=False, unique=True
    )
    adr_cop: Mapped[float] = mapped_column(postgresql.NUMERIC, nullable=False)
    adr_usd: Mapped[float] = mapped_column(postgresql.NUMERIC, nullable=True)
    annual_revenue_cop: Mapped[float] = mapped_column(
        postgresql.NUMERIC, nullable=False
    )
    annual_revenue_usd: Mapped[float] = mapped_column(postgresql.NUMERIC, nullable=True)
    bedrooms: Mapped[int] = mapped_column(postgresql.INTEGER, nullable=False)
    latitude: Mapped[float] = mapped_column(postgresql.REAL, nullable=False)
    location: Mapped[WKBElement] = mapped_column(
        Geography(geometry_type="POINT", srid=4326, spatial_index=True), nullable=False
    )
    longitude: Mapped[float] = mapped_column(postgresql.REAL, nullable=False)
    market_id: Mapped[UUID] = mapped_column(ForeignKey("markets.id"), nullable=True)
    occupancy_rate: Mapped[float] = mapped_column(postgresql.REAL, nullable=False)
    property_type: Mapped[str] = mapped_column(postgresql.TEXT, nullable=False)
    source_url: Mapped[str] = mapped_column(postgresql.TEXT, nullable=False)

    __table_args__ = (
        Index(
            "ix_listings_location",
            "location",
            postgresql_using="gist",
        ),
    )
