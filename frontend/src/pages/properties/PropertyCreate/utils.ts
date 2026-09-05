import type { PropertyCreateRequest } from '@/types';

/**
 * Everything the manual-entry panel collects, as strings so every field is a
 * controlled `TextField` - parsed to the right type only when building the
 * request body.
 */
export type ManualEntryValues = {
  address: string;
  bedrooms: string;
  city: string;
  country: string;
  latitude: number | null;
  longitude: number | null;
  neighborhood: string;
  property_type: string;
  state: string;
  postal_code: string;
  purchase_price_cop: string;
  status: string;
  name: string;
  description: string;
  notes: string;
};

export const EMPTY_MANUAL_ENTRY_VALUES: ManualEntryValues = {
  address: '',
  bedrooms: '',
  city: '',
  country: 'Colombia',
  latitude: null,
  longitude: null,
  neighborhood: '',
  property_type: '',
  state: '',
  postal_code: '',
  purchase_price_cop: '',
  status: '',
  name: '',
  description: '',
  notes: '',
};

/**
 * Mirrors `MANUAL_FIELDS`' all-or-nothing rule on the backend: every one of the
 * nine fields must be present before the manual path is allowed to submit, so a
 * partial entry is caught here rather than spending a round trip on a 422.
 */
export function isManualEntryComplete(values: ManualEntryValues): boolean {
  return (
    values.address.trim() !== '' &&
    values.bedrooms.trim() !== '' &&
    Number.isFinite(Number(values.bedrooms)) &&
    values.city.trim() !== '' &&
    values.country.trim() !== '' &&
    values.latitude != null &&
    values.longitude != null &&
    values.neighborhood.trim() !== '' &&
    values.property_type.trim() !== '' &&
    values.state.trim() !== ''
  );
}

export function buildManualCreateRequest(
  sourceUrl: string,
  values: ManualEntryValues,
): PropertyCreateRequest {
  return {
    source_url: sourceUrl,
    address: values.address,
    bedrooms: Number(values.bedrooms),
    city: values.city,
    country: values.country,
    latitude: values.latitude,
    longitude: values.longitude,
    neighborhood: values.neighborhood,
    property_type: values.property_type,
    state: values.state,
    postal_code: values.postal_code.trim() === '' ? null : values.postal_code,
    purchase_price_cop:
      values.purchase_price_cop.trim() === ''
        ? null
        : Number(values.purchase_price_cop),
    status: values.status.trim() === '' ? null : values.status,
    name: values.name.trim() === '' ? null : values.name,
    description: values.description.trim() === '' ? null : values.description,
    notes: values.notes.trim() === '' ? null : values.notes,
  };
}
