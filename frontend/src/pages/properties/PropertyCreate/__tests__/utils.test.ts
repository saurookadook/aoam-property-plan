import { describe, expect, it } from 'vitest';

import {
  buildManualCreateRequest,
  EMPTY_MANUAL_ENTRY_VALUES,
  isManualEntryComplete,
  type ManualEntryValues,
} from '../utils';

const COMPLETE_VALUES: ManualEntryValues = {
  ...EMPTY_MANUAL_ENTRY_VALUES,
  address: 'Vereda Cocora 12-40',
  bedrooms: '3',
  city: 'Salento',
  country: 'Colombia',
  latitude: 4.6389,
  longitude: -75.5701,
  neighborhood: 'Cocora',
  property_type: 'House',
  state: 'Quindío',
};

describe('isManualEntryComplete', () => {
  it('is false when every field is empty', () => {
    expect(isManualEntryComplete(EMPTY_MANUAL_ENTRY_VALUES)).toBe(false);
  });

  it('is false when only lat/lng are missing', () => {
    expect(
      isManualEntryComplete({ ...COMPLETE_VALUES, latitude: null, longitude: null }),
    ).toBe(false);
  });

  it('is false when bedrooms is not numeric', () => {
    expect(isManualEntryComplete({ ...COMPLETE_VALUES, bedrooms: 'three' })).toBe(
      false,
    );
  });

  it('is true once every required field is present', () => {
    expect(isManualEntryComplete(COMPLETE_VALUES)).toBe(true);
  });
});

describe('buildManualCreateRequest', () => {
  it('parses numeric fields and drops blank optional fields to null', () => {
    const request = buildManualCreateRequest(
      'https://www.fincaraiz.com.co/inmueble/finca-cocora-salento',
      COMPLETE_VALUES,
    );

    expect(request).toEqual({
      source_url: 'https://www.fincaraiz.com.co/inmueble/finca-cocora-salento',
      address: 'Vereda Cocora 12-40',
      bedrooms: 3,
      city: 'Salento',
      country: 'Colombia',
      latitude: 4.6389,
      longitude: -75.5701,
      neighborhood: 'Cocora',
      property_type: 'House',
      state: 'Quindío',
      postal_code: null,
      purchase_price_cop: null,
      status: null,
      name: null,
      description: null,
      notes: null,
    });
  });

  it('carries the optional fields through when supplied', () => {
    const request = buildManualCreateRequest('https://example.com/off-market', {
      ...COMPLETE_VALUES,
      purchase_price_cop: '850000000',
      name: 'Finca Cocora',
      status: 'active',
    });

    expect(request.purchase_price_cop).toBe(850000000);
    expect(request.name).toBe('Finca Cocora');
    expect(request.status).toBe('active');
  });
});
