import { describe, expect, it } from 'vitest';

import type {
  MarketFinancialReportEntity,
  MarketWithFinancialReportEntity,
} from '@/types';
import { sortMarkets } from '../sortMarkets';

function buildMarket(
  locality: string,
  overrides: Partial<MarketFinancialReportEntity> | null,
): MarketWithFinancialReportEntity {
  return {
    id: `${locality}-id`,
    created_at: '2026-07-29T01:46:56.335735Z',
    updated_at: '2026-08-20T02:06:09.952335Z',
    country: 'Colombia',
    district: null,
    locality,
    region: 'region',
    latitude: null,
    longitude: null,
    financial_report:
      overrides == null
        ? null
        : {
            id: `${locality}-report`,
            created_at: '2026-07-29T01:46:56.335735Z',
            updated_at: '2026-08-20T02:06:09.952335Z',
            market_id: `${locality}-id`,
            adr_cop: 0,
            adr_usd: null,
            annual_revenue_cop: 0,
            annual_revenue_usd: null,
            last_updated: '2026-08-20T02:06:09.952335Z',
            listing_count: 100,
            monthly_revenue_distribution: null,
            occupancy_rate: 0,
            peak_months: null,
            ...overrides,
          },
  };
}

describe('sortMarkets', () => {
  const pance = buildMarket('Pance', {
    adr_cop: 401_200,
    annual_revenue_cop: 27_840_000,
    listing_count: 27.8,
    occupancy_rate: 0.33,
  });
  const calima = buildMarket('Calima', {
    adr_cop: 857_200,
    annual_revenue_cop: 31_680_000,
    listing_count: 178.3,
    occupancy_rate: 0.182,
  });
  const salento = buildMarket('Salento', {
    adr_cop: 340_400,
    annual_revenue_cop: 25_920_000,
    listing_count: 514.6,
    occupancy_rate: 0.342,
  });
  const bogota = buildMarket('Bogota', {
    adr_cop: 188_400,
    annual_revenue_cop: 16_800_000,
    listing_count: 6375.8,
    occupancy_rate: 0.402,
  });
  const santaMarta = buildMarket('Santa Marta', null);

  const markets = [santaMarta, bogota, salento, calima, pance];

  it('sorts by fit score, descending, reproducing the plan sanity table', () => {
    const sorted = sortMarkets(markets, 'fit');

    expect(sorted.map((market) => market.locality)).toEqual([
      'Pance',
      'Calima',
      'Salento',
      'Bogota',
      'Santa Marta',
    ]);
  });

  it('sorts by ADR, descending', () => {
    const sorted = sortMarkets(markets, 'adr');

    expect(sorted.map((market) => market.locality)).toEqual([
      'Calima',
      'Pance',
      'Salento',
      'Bogota',
      'Santa Marta',
    ]);
  });

  it('sorts by occupancy, descending', () => {
    const sorted = sortMarkets(markets, 'occupancy');

    expect(sorted.map((market) => market.locality)).toEqual([
      'Bogota',
      'Salento',
      'Pance',
      'Calima',
      'Santa Marta',
    ]);
  });

  it('sorts by revenue, descending', () => {
    const sorted = sortMarkets(markets, 'revenue');

    expect(sorted.map((market) => market.locality)).toEqual([
      'Calima',
      'Pance',
      'Salento',
      'Bogota',
      'Santa Marta',
    ]);
  });

  it('always pushes a report-less market to the end, regardless of sortKey', () => {
    for (const sortKey of ['fit', 'adr', 'occupancy', 'revenue'] as const) {
      const sorted = sortMarkets(markets, sortKey);
      expect(sorted.at(-1)?.locality).toBe('Santa Marta');
    }
  });

  it('does not mutate the input array', () => {
    const copy = [...markets];
    sortMarkets(markets, 'adr');
    expect(markets).toEqual(copy);
  });
});
