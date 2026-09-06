import type { PropertyCreateRequest } from '@/types';
import { isNonEmptyString } from '@/common/utils';

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
  description: string;
  latitude: number | null;
  longitude: number | null;
  name: string;
  neighborhood: string;
  notes: string;
  postal_code: string;
  property_type: string;
  purchase_price_cop: string;
  state: string;
  status: string;
};

export const EMPTY_MANUAL_ENTRY_VALUES: ManualEntryValues = {
  address: '',
  bedrooms: '',
  city: '',
  country: 'Colombia',
  description: '',
  latitude: null,
  longitude: null,
  name: '',
  neighborhood: '',
  notes: '',
  postal_code: '',
  property_type: '',
  purchase_price_cop: '',
  state: '',
  status: '',
};

/**
 * Mirrors `MANUAL_FIELDS`' all-or-nothing rule on the backend: every one of the
 * nine fields must be present before the manual path is allowed to submit, so a
 * partial entry is caught here rather than spending a round trip on a 422.
 */
export function isManualEntryComplete(values: ManualEntryValues): boolean {
  return (
    isNonEmptyString(values.address.trim()) &&
    isNonEmptyString(values.bedrooms.trim()) &&
    Number.isFinite(Number(values.bedrooms)) &&
    isNonEmptyString(values.city.trim()) &&
    isNonEmptyString(values.country.trim()) &&
    values.latitude != null &&
    values.longitude != null &&
    isNonEmptyString(values.neighborhood.trim()) &&
    isNonEmptyString(values.property_type.trim()) &&
    isNonEmptyString(values.state.trim())
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
    description: isNonEmptyString(values.description.trim())
      ? values.description
      : null,
    latitude: values.latitude,
    longitude: values.longitude,
    name: isNonEmptyString(values.name.trim()) ? values.name : null,
    neighborhood: values.neighborhood,
    notes: isNonEmptyString(values.notes.trim()) ? values.notes : null,
    postal_code: isNonEmptyString(values.postal_code.trim())
      ? values.postal_code
      : null,
    property_type: values.property_type,
    purchase_price_cop: isNonEmptyString(values.purchase_price_cop.trim())
      ? Number(values.purchase_price_cop)
      : null,
    state: values.state,
    status: isNonEmptyString(values.status.trim()) ? values.status : null,
  };
}
