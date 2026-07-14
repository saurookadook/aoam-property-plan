from __future__ import annotations

from typing import Optional
from uuid import UUID

from models.base.entity import BaseEntityModel

# from models.listing.entity import ListingEntity
from models.mixins import TimestampsEntityMixin


class ListingFinancialReportEntity(BaseEntityModel, TimestampsEntityMixin):
    listing_id: UUID
    # listing: Optional[ListingEntity] = None
    # adr_cop: float
    # adr_usd: Optional[float]
    # annual_revenue_cop: float
    # annual_revenue_usd: Optional[float]
    # occupancy_rate: float
    number_of_reviews: Optional[int]
    rating_overall: Optional[float]
    rating_accuracy: Optional[float]
    rating_checkin: Optional[float]
    rating_cleanliness: Optional[float]
    rating_communication: Optional[float]
    rating_location: Optional[float]
    rating_value: Optional[float]
    ttm_revenue: Optional[float]
    ttm_avg_rate: Optional[float]
    ttm_occupancy_rate: Optional[float]
    ttm_adjusted_occupancy_rate: Optional[float]
    ttm_revpar: Optional[float]
    ttm_adjusted_revpar: Optional[float]
    ttm_total_days: Optional[float]
    ttm_available_days: Optional[float]
    ttm_blocked_days: Optional[float]
    ttm_days_reserved: Optional[float]
    ttm_avg_min_nights: Optional[float]
    ttm_avg_length_of_stay: Optional[float]
    l90d_revenue: Optional[float]
    l90d_avg_rate: Optional[float]
    l90d_occupancy_rate: Optional[float]
    l90d_adjusted_occupancy_rate: Optional[float]
    l90d_revpar: Optional[float]
    l90d_adjusted_revpar: Optional[float]
    l90d_total_days: Optional[float]
    l90d_available_days: Optional[float]
    l90d_blocked_days: Optional[float]
    l90d_days_reserved: Optional[float]
    l90d_avg_min_nights: Optional[float]
    l90d_avg_length_of_stay: Optional[float]
