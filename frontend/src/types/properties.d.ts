import type { BaseEntity } from './entity';

/**
 * Mirrors `models/property/entity.PropertyEntity` field-for-field.
 *
 * `Optional[X]` becomes `X | null` rather than `X?` throughout: the API sends an
 * explicit `null` for an absent value, and `X?` would let `undefined` through a
 * `!= null` check that the served payload never produces.
 */
export type PropertyEntity = BaseEntity & {
  address: string;
  amenities: string[];
  baths: number | null;
  bedrooms: number;
  city: string;
  country: string;
  description: string | null;
  guests: number | null;
  latitude: number;
  longitude: number;
  market_id: string | null;
  name: string | null;
  neighborhood: string;
  notes: string | null;
  postal_code: string | null;
  property_type: string;
  purchase_price_cop: number | null;
  purchase_price_usd: number | null;
  source_created_at: string;
  source_url: string;
  state: string;
  status: string;
};

/** One of the all-or-nothing manual-entry fields on `PropertyCreateRequest`. */
export type ManualPropertyField =
  | 'address'
  | 'bedrooms'
  | 'city'
  | 'country'
  | 'latitude'
  | 'longitude'
  | 'neighborhood'
  | 'property_type'
  | 'state';

/**
 * Mirrors `api/models/property.PropertyCreateRequest`.
 *
 * `source_url` is required either way. Supplying every `ManualPropertyField`
 * stores the body as given; supplying none of them scrapes `source_url`. A
 * partial manual set is a 422.
 */
export type PropertyCreateRequest = {
  source_url: string;

  // --- manual entry: all of these, or none of them
  address?: string | null;
  bedrooms?: number | null;
  city?: string | null;
  country?: string | null;
  latitude?: number | null;
  longitude?: number | null;
  neighborhood?: string | null;
  property_type?: string | null;
  state?: string | null;

  // --- manual entry only
  postal_code?: string | null;
  purchase_price_cop?: number | null;
  source_created_at?: string | null;
  status?: string | null;

  // --- valid on either path
  amenities?: string[] | null;
  description?: string | null;
  name?: string | null;
  notes?: string | null;
};
