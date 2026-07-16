from __future__ import annotations

from typing import Optional
from uuid import UUID

from geoalchemy2 import Geography, WKBElement
from sqlalchemy import ForeignKey, Index
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base_db import BaseDB
from models.listing_financial_report.db import ListingFinancialReportDB
from models.mixins import TimestampsDB


class ListingDB(BaseDB, TimestampsDB):
    airroi_id: Mapped[int] = mapped_column(
        postgresql.BIGINT, nullable=False, unique=True
    )
    amenities: Mapped[list[str]] = mapped_column(
        postgresql.ARRAY(postgresql.TEXT), nullable=False, server_default="{}"
    )
    baths: Mapped[Optional[float]] = mapped_column(postgresql.REAL, nullable=True)
    beds: Mapped[Optional[int]] = mapped_column(postgresql.INTEGER, nullable=True)
    bedrooms: Mapped[int] = mapped_column(postgresql.INTEGER, nullable=False)
    cover_photo_url: Mapped[Optional[str]] = mapped_column(
        postgresql.TEXT, nullable=True
    )
    description: Mapped[Optional[str]] = mapped_column(postgresql.TEXT, nullable=True)
    latitude: Mapped[float] = mapped_column(postgresql.DOUBLE_PRECISION, nullable=False)
    location: Mapped[WKBElement] = mapped_column(
        Geography(geometry_type="POINT", srid=4326, spatial_index=True), nullable=False
    )
    longitude: Mapped[float] = mapped_column(
        postgresql.DOUBLE_PRECISION, nullable=False
    )
    market_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("markets.id"), nullable=True
    )
    name: Mapped[Optional[str]] = mapped_column(postgresql.TEXT, nullable=True)
    photo_urls: Mapped[list[str]] = mapped_column(
        postgresql.ARRAY(postgresql.TEXT), nullable=False, server_default="{}"
    )
    property_type: Mapped[str] = mapped_column(postgresql.TEXT, nullable=False)
    source_url: Mapped[Optional[str]] = mapped_column(postgresql.TEXT, nullable=True)

    listing_financial_reports: Mapped[list[ListingFinancialReportDB]] = relationship(
        back_populates="listing"
    )

    __table_args__ = (
        Index(
            "ix_listings_location",
            "location",
            postgresql_using="gist",
        ),
    )
