import type { MarketWithFinancialReportEntity } from '@/types';

/**
 * A derived heuristic, not a datum. Every consumer must label it as such.
 *
 * The anchors are **absolute and in COP**, deliberately. COP because `adr_usd`
 * and `annual_revenue_usd` are NULL in every served row, and because a
 * rate-dependent score would silently reorder the list between renders.
 * Absolute rather than min-max because a min-max score always pins one market at
 * 100, tells you only which served row is least bad, reorders every other market
 * when one is added, and makes every unit test depend on the whole fixture set.
 *
 * @note These anchors are a calibration constant. They were chosen against the
 * four originally seeded markets, and are the thing to revisit once the four
 * markets added in chunk 1 have been ingested and the real range is known.
 */
export const FIT_ANCHORS = {
  /** ≈ $3,000 – $15,000 a year. */
  annualRevenueCop: { lo: 12_000_000, hi: 60_000_000 },
  occupancyRate: { lo: 0.15, hi: 0.55 },
  /** ≈ $30 – $220 a night. */
  adrCop: { lo: 120_000, hi: 880_000 },
  /** Saturation is logarithmic, so depth is scored on a log scale. */
  listingCount: { lo: 50, hi: 10_000 },
} as const;

export const FIT_WEIGHTS = {
  revenue: 0.4,
  occupancy: 0.3,
  adr: 0.15,
  depth: 0.15,
} as const;

/**
 * Below this, "no competition" and "no market" are indistinguishable from the
 * depth term alone - Pance's 27.8 listings score a perfect 1.0 on depth.
 */
export const THIN_MARKET_LISTING_COUNT = 30;

export type InvestmentFit = {
  score: number;
  /**
   * A flag, **not an adjustment**. State the number, state how much to trust it,
   * never silently move it.
   */
  isThinMarket: boolean;
  listingCount: number | null;
  components: {
    revenue: number;
    occupancy: number;
    adr: number;
    depth: number;
  };
};

export function clamp(value: number, lo: number, hi: number): number {
  return Math.min(Math.max(value, lo), hi);
}

export function norm(value: number, lo: number, hi: number): number {
  if (hi === lo) {
    return 0;
  }

  return clamp((value - lo) / (hi - lo), 0, 1);
}

/**
 * `null` for a market with no financial report - a fresh roster entry has none
 * until the ingest cron has run, and inventing a zero would sort it below
 * markets we have actually measured as poor.
 */
export function investmentFit(
  market: Pick<MarketWithFinancialReportEntity, 'financial_report'>,
): InvestmentFit | null {
  const report = market.financial_report;

  if (report == null) {
    return null;
  }

  const revenue = norm(
    report.annual_revenue_cop,
    FIT_ANCHORS.annualRevenueCop.lo,
    FIT_ANCHORS.annualRevenueCop.hi,
  );
  const occupancy = norm(
    report.occupancy_rate,
    FIT_ANCHORS.occupancyRate.lo,
    FIT_ANCHORS.occupancyRate.hi,
  );
  const adr = norm(report.adr_cop, FIT_ANCHORS.adrCop.lo, FIT_ANCHORS.adrCop.hi);
  const depth = depthScore(report.listing_count);

  const score = Math.round(
    100 *
      (FIT_WEIGHTS.revenue * revenue +
        FIT_WEIGHTS.occupancy * occupancy +
        FIT_WEIGHTS.adr * adr +
        FIT_WEIGHTS.depth * depth),
  );

  return {
    score,
    isThinMarket: report.listing_count < THIN_MARKET_LISTING_COUNT,
    listingCount: report.listing_count,
    components: { revenue, occupancy, adr, depth },
  };
}

/** Inverse-log: more listings is more competition, with diminishing effect. */
export function depthScore(listingCount: number): number {
  const { lo, hi } = FIT_ANCHORS.listingCount;
  const value = Math.log10(Math.max(listingCount, 1));

  return clamp(1 - (value - Math.log10(lo)) / (Math.log10(hi) - Math.log10(lo)), 0, 1);
}

/**
 * The median asking price across a market's saved properties, or `null` below
 * three priced rows.
 *
 * Three is the point at which a median stops being "one listing, restated".
 * Returning `null` rather than a figure is what lets the budget indicator say
 * "Not enough price data (N)" instead of extrapolating from a single outlier.
 */
export const MIN_PRICED_PROPERTIES = 3;

/** A usable price: not null, finite, and positive. Shared with `BudgetIndicator`'s count. */
export function filterPricedValues(
  prices: readonly (number | null | undefined)[],
): number[] {
  return prices.filter(
    (price): price is number => price != null && Number.isFinite(price) && price > 0,
  );
}

export function medianPurchasePriceCop(
  purchasePrices: readonly (number | null | undefined)[],
): number | null {
  const priced = filterPricedValues(purchasePrices).sort((a, b) => a - b);

  if (priced.length < MIN_PRICED_PROPERTIES) {
    return null;
  }

  const middle = Math.floor(priced.length / 2);

  return priced.length % 2 === 0
    ? (priced[middle - 1] + priced[middle]) / 2
    : priced[middle];
}
