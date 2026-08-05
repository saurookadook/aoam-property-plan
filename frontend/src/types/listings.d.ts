import type { BaseEntity } from './entity';

export type ListingEntity = BaseEntity & {
  airroi_id: string;
  amenities: string[];
  baths?: number;
  beds?: number;
  bedrooms: number;
  cover_photo_url: string;
  description?: string;
  latitude: number;
  location: string;
  longitude: number;
  market_id?: string;
  name?: string;
  photo_urls: string[];
  property_type: string;
  source_url?: string;

  listing_financial_reports: ListingFinancialReportEntity[];
};

export type ListingFinancialReportEntity = BaseEntity & {
  number_of_reviews?: number;
  rating_overall?: number;
  rating_accuracy?: number;
  rating_checkin?: number;
  rating_cleanliness?: number;
  rating_communication?: number;
  rating_location?: number;
  rating_value?: number;
  ttm_revenue?: number;
  ttm_avg_rate?: number;
  ttm_occupancy_rate?: number;
  ttm_adjusted_occupancy_rate?: number;
  ttm_revpar?: number;
  ttm_adjusted_revpar?: number;
  ttm_total_days?: number;
  ttm_available_days?: number;
  ttm_blocked_days?: number;
  ttm_days_reserved?: number;
  ttm_avg_min_nights?: number;
  ttm_avg_length_of_stay?: number;
  l90d_revenue?: number;
  l90d_avg_rate?: number;
  l90d_occupancy_rate?: number;
  l90d_adjusted_occupancy_rate?: number;
  l90d_revpar?: number;
  l90d_adjusted_revpar?: number;
  l90d_total_days?: number;
  l90d_available_days?: number;
  l90d_blocked_days?: number;
  l90d_days_reserved?: number;
  l90d_avg_min_nights?: number;
  l90d_avg_length_of_stay?: number;
};

export type HighestEarningListingEntity = BaseEntity & {
  cover_photo_url?: string;
  market_id: string;
  name: string;
  // ----- from `listing_financial_reports`
  // trailing twelve months (ttm)
  ttm_revenue: number;
  // ----- from `markets`
  country: string;
  locality: string;
  region: string;
};

export type NewestListingEntity = BaseEntity & {
  cover_photo_url: string;
  market_id: string;
  name: string;
};
