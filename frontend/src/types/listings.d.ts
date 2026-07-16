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
  // airroiId: string;
  // bedrooms: number;
  // coverPhotoUrl: string;
  // latitude: number;
  // location: string;
  // longitude: number;
  // marketId?: string;
  // propertyType: string;
  // sourceUrl?: string;
};
