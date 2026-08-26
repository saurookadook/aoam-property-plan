import { describe, expect, it } from 'vitest';

import type {
  MarketFinancialReportEntity,
  MarketWithFinancialReportEntity,
} from '@/types';
import {
  MIN_PRICED_PROPERTIES,
  depthScore,
  investmentFit,
  medianPurchasePriceCop,
  norm,
} from '../investmentFit';

function buildMarket({
  adrCop,
  annualRevenueCop,
  listingCount,
  occupancyRate,
}: {
  adrCop: number;
  annualRevenueCop: number;
  listingCount: number;
  occupancyRate: number;
}): Pick<MarketWithFinancialReportEntity, 'financial_report'> {
  const financialReport: MarketFinancialReportEntity = {
    id: 'report-id',
    created_at: '2026-07-29T01:46:56.335735Z',
    updated_at: '2026-08-20T02:06:09.952335Z',
    market_id: 'market-id',
    adr_cop: adrCop,
    adr_usd: null,
    annual_revenue_cop: annualRevenueCop,
    annual_revenue_usd: null,
    last_updated: '2026-08-20T02:06:09.952335Z',
    listing_count: listingCount,
    monthly_revenue_distribution: null,
    occupancy_rate: occupancyRate,
    peak_months: null,
  };

  return { financial_report: financialReport };
}

/** The four originally seeded markets, from the plan's sanity-check table. */
const SEEDED_MARKETS = {
  pance: buildMarket({
    adrCop: 401_200,
    annualRevenueCop: 27_840_000,
    listingCount: 27.8,
    occupancyRate: 0.33,
  }),
  calima: buildMarket({
    adrCop: 857_200,
    annualRevenueCop: 31_680_000,
    listingCount: 178.3,
    occupancyRate: 0.182,
  }),
  salento: buildMarket({
    adrCop: 340_400,
    annualRevenueCop: 25_920_000,
    listingCount: 514.6,
    occupancyRate: 0.342,
  }),
  bogota: buildMarket({
    adrCop: 188_400,
    annualRevenueCop: 16_800_000,
    listingCount: 6375.8,
    occupancyRate: 0.402,
  }),
};

describe('norm', () => {
  it('clamps outside the anchor band rather than extrapolating', () => {
    expect(norm(5, 10, 20)).toBe(0);
    expect(norm(25, 10, 20)).toBe(1);
    expect(norm(15, 10, 20)).toBe(0.5);
  });
});

describe('depthScore', () => {
  it('scores an empty market at 1 and a saturated one at 0', () => {
    expect(depthScore(0)).toBe(1);
    expect(depthScore(50)).toBe(1);
    expect(depthScore(10_000)).toBe(0);
    expect(depthScore(50_000)).toBe(0);
  });

  it('falls logarithmically between the anchors', () => {
    // The geometric midpoint of 50 and 10,000.
    expect(depthScore(Math.sqrt(50 * 10_000))).toBeCloseTo(0.5, 10);
  });
});

describe('investmentFit', () => {
  it.each([
    ['Pance', SEEDED_MARKETS.pance, 47],
    ['Calima', SEEDED_MARKETS.calima, 45],
    ['Salento', SEEDED_MARKETS.salento, 39],
    ['Bogota', SEEDED_MARKETS.bogota, 26],
  ])('scores %s at %i', (_label, market, expected) => {
    expect(investmentFit(market)?.score).toBe(expected);
  });

  it("reproduces the doc's Part 1 ranking", () => {
    const ranked = Object.entries(SEEDED_MARKETS)
      .map(([name, market]) => ({ name, score: investmentFit(market)?.score ?? -1 }))
      .sort((a, b) => b.score - a.score)
      .map(({ name }) => name);

    expect(ranked).toEqual(['pance', 'calima', 'salento', 'bogota']);
  });

  it('flags a thin market without adjusting its depth score', () => {
    const fit = investmentFit(SEEDED_MARKETS.pance);

    expect(fit?.isThinMarket).toBe(true);
    // The flag states the problem; it does not quietly move the number. Pance
    // still scores a perfect 1.0 on depth, and the badge says why that is
    // misleading.
    expect(fit?.components.depth).toBe(1);
  });

  it('does not flag a market above the thin threshold', () => {
    expect(investmentFit(SEEDED_MARKETS.calima)?.isThinMarket).toBe(false);
  });

  it('returns null for a market that has never been summarised', () => {
    // A freshly seeded roster entry. Scoring it zero would sort it below markets
    // we have actually measured as poor.
    expect(investmentFit({ financial_report: null })).toBeNull();
  });
});

describe('medianPurchasePriceCop', () => {
  it('returns the middle value of an odd-length set', () => {
    expect(medianPurchasePriceCop([690_000_000, 850_000_000, 1_120_000_000])).toBe(
      850_000_000,
    );
  });

  it('averages the middle pair of an even-length set', () => {
    expect(
      medianPurchasePriceCop([690_000_000, 850_000_000, 1_120_000_000, 1_400_000_000]),
    ).toBe(985_000_000);
  });

  it('ignores unpriced rows when counting toward the threshold', () => {
    // Two priced rows plus two nulls is still two priced rows.
    expect(
      medianPurchasePriceCop([690_000_000, null, 850_000_000, undefined]),
    ).toBeNull();
  });

  it(`returns null below ${MIN_PRICED_PROPERTIES} priced rows`, () => {
    // A "median" over one or two listings is one listing, restated.
    expect(medianPurchasePriceCop([850_000_000, 690_000_000])).toBeNull();
  });

  it('discards non-positive prices', () => {
    expect(
      medianPurchasePriceCop([0, -1, 690_000_000, 850_000_000, 1_120_000_000]),
    ).toBe(850_000_000);
  });
});
