from __future__ import annotations

from uuid import UUID

from geoalchemy2 import Geography, WKBElement
from sqlalchemy import ForeignKey, Index
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base_db import BaseDB
from models.mixins import TimestampsDB


class ListingDB(BaseDB, TimestampsDB):
    from models.listing_financial_report.db import ListingFinancialReportDB

    airroi_id: Mapped[int] = mapped_column(
        postgresql.BIGINT, nullable=False, unique=True
    )
    bedrooms: Mapped[int] = mapped_column(postgresql.INTEGER, nullable=False)
    cover_photo_url: Mapped[str] = mapped_column(postgresql.TEXT, nullable=True)
    latitude: Mapped[float] = mapped_column(postgresql.DOUBLE_PRECISION, nullable=False)
    location: Mapped[WKBElement] = mapped_column(
        Geography(geometry_type="POINT", srid=4326, spatial_index=True), nullable=False
    )
    longitude: Mapped[float] = mapped_column(
        postgresql.DOUBLE_PRECISION, nullable=False
    )
    market_id: Mapped[UUID] = mapped_column(ForeignKey("markets.id"), nullable=True)
    property_type: Mapped[str] = mapped_column(postgresql.TEXT, nullable=False)
    source_url: Mapped[str] = mapped_column(postgresql.TEXT, nullable=True)

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
