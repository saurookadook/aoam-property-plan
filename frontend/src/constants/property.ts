import type { ManualPropertyField } from '@/types';

/**
 * Mirrors `MANUAL_FIELDS` in `api/models/property.py`.
 *
 * The backend's validator is all-or-nothing: supply every one of these and the
 * body is stored as given, supply none and `source_url` is scraped, supply some
 * and the request is a 422. The form needs the list at runtime to enforce the
 * same rule before it spends a round trip, which is why this is a `.ts` constant
 * rather than a declaration in `types/properties.d.ts`.
 */
export const MANUAL_FIELDS = [
  'address',
  'bedrooms',
  'city',
  'country',
  'latitude',
  'longitude',
  'neighborhood',
  'property_type',
  'state',
] as const satisfies readonly ManualPropertyField[];

/** Accepted only alongside a full manual entry - scraping reads these off the page. */
export const MANUAL_OPTIONAL_FIELDS = [
  'postal_code',
  'purchase_price_cop',
  'source_created_at',
  'status',
] as const;

/** Valid on either path, so they take no part in deciding which one applies. */
export const OVERRIDE_FIELDS = ['amenities', 'description', 'name', 'notes'] as const;
