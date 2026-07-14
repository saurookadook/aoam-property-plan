from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base_db import BaseDB
from models.mixins import TimestampsDB

if TYPE_CHECKING:
    from models.listing.db import ListingDB


class ListingFinancialReportDB(BaseDB, TimestampsDB):
    listing_id: Mapped[UUID] = mapped_column(ForeignKey("listings.id"), nullable=False)
    listing: Mapped["ListingDB"] = relationship(
        "ListingDB", back_populates="listing_financial_reports"
    )

    # adr_cop: Mapped[float] = mapped_column(postgresql.NUMERIC, nullable=False)
    # adr_usd: Mapped[float] = mapped_column(postgresql.NUMERIC, nullable=True)
    # annual_revenue_cop: Mapped[float] = mapped_column(
    #     postgresql.NUMERIC, nullable=False
    # )
    # annual_revenue_usd: Mapped[float] = mapped_column(postgresql.NUMERIC, nullable=True)
    # occupancy_rate: Mapped[float] = mapped_column(postgresql.REAL, nullable=False)
    # Ratings
    number_of_reviews: Mapped[int] = mapped_column(postgresql.INTEGER, nullable=True)
    rating_overall: Mapped[float] = mapped_column(postgresql.REAL, nullable=True)
    rating_accuracy: Mapped[float] = mapped_column(postgresql.REAL, nullable=True)
    rating_checkin: Mapped[float] = mapped_column(postgresql.REAL, nullable=True)
    rating_cleanliness: Mapped[float] = mapped_column(postgresql.REAL, nullable=True)
    rating_communication: Mapped[float] = mapped_column(postgresql.REAL, nullable=True)
    rating_location: Mapped[float] = mapped_column(postgresql.REAL, nullable=True)
    rating_value: Mapped[float] = mapped_column(postgresql.REAL, nullable=True)
    # Performance Metrics
    ttm_revenue: Mapped[float] = mapped_column(postgresql.NUMERIC, nullable=True)
    ttm_avg_rate: Mapped[float] = mapped_column(postgresql.NUMERIC, nullable=True)
    ttm_occupancy_rate: Mapped[float] = mapped_column(postgresql.REAL, nullable=True)
    ttm_adjusted_occupancy_rate: Mapped[float] = mapped_column(
        postgresql.REAL, nullable=True
    )
    ttm_revpar: Mapped[float] = mapped_column(postgresql.NUMERIC, nullable=True)
    ttm_adjusted_revpar: Mapped[float] = mapped_column(
        postgresql.NUMERIC, nullable=True
    )
    ttm_total_days: Mapped[float] = mapped_column(postgresql.REAL, nullable=True)
    ttm_available_days: Mapped[float] = mapped_column(postgresql.REAL, nullable=True)
    ttm_blocked_days: Mapped[float] = mapped_column(postgresql.REAL, nullable=True)
    ttm_days_reserved: Mapped[float] = mapped_column(postgresql.REAL, nullable=True)
    ttm_avg_min_nights: Mapped[float] = mapped_column(postgresql.REAL, nullable=True)
    ttm_avg_length_of_stay: Mapped[float] = mapped_column(
        postgresql.REAL, nullable=True
    )
    l90d_revenue: Mapped[float] = mapped_column(postgresql.NUMERIC, nullable=True)
    l90d_avg_rate: Mapped[float] = mapped_column(postgresql.NUMERIC, nullable=True)
    l90d_occupancy_rate: Mapped[float] = mapped_column(postgresql.REAL, nullable=True)
    l90d_adjusted_occupancy_rate: Mapped[float] = mapped_column(
        postgresql.REAL, nullable=True
    )
    l90d_revpar: Mapped[float] = mapped_column(postgresql.NUMERIC, nullable=True)
    l90d_adjusted_revpar: Mapped[float] = mapped_column(
        postgresql.NUMERIC, nullable=True
    )
    l90d_total_days: Mapped[float] = mapped_column(postgresql.REAL, nullable=True)
    l90d_available_days: Mapped[float] = mapped_column(postgresql.REAL, nullable=True)
    l90d_blocked_days: Mapped[float] = mapped_column(postgresql.REAL, nullable=True)
    l90d_days_reserved: Mapped[float] = mapped_column(postgresql.REAL, nullable=True)
    l90d_avg_min_nights: Mapped[float] = mapped_column(postgresql.REAL, nullable=True)
    l90d_avg_length_of_stay: Mapped[float] = mapped_column(
        postgresql.REAL, nullable=True
    )
