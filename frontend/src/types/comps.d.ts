import type { BaseEntity } from './entity';

/**
 * Mirrors `models/listing/entity.CompListingEntity` - just enough of a listing
 * to render one row of a comp table.
 */
export type CompListingEntity = {
  id: string;
  airroi_id: number;
  baths: number | null;
  bedrooms: number;
  cover_photo_url: string | null;
  latitude: number;
  longitude: number;
  name: string | null;
  property_type: string;
  source_url: string | null;
};

/** Mirrors `models/property_comp/entity.PropertyCompEntity`. */
export type PropertyCompEntity = BaseEntity & {
  adr_cop: number | null;
  captured_at: string;
  distance_km: number | null;
  listing_id: string;
  occupancy_rate: number | null;
  property_id: string;
  ttm_revenue_cop: number | null;
  ttm_total_days: number | null;
};

/**
 * Mirrors `models/property_comp/entity.PropertyCompWithListingEntity`, which
 * both comps routes serve.
 */
export type PropertyCompWithListingEntity = PropertyCompEntity & {
  listing: CompListingEntity | null;
};
