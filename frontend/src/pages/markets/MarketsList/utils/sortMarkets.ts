import type { MarketWithFinancialReportEntity } from '@/types';
import { investmentFit } from '@/common/utils/investmentFit';

export type MarketSortKey = 'fit' | 'adr' | 'occupancy' | 'revenue';

export const MARKET_SORT_OPTIONS: { key: MarketSortKey; label: string }[] = [
  { key: 'fit', label: 'Fit' },
  { key: 'adr', label: 'ADR' },
  { key: 'occupancy', label: 'Occupancy' },
  { key: 'revenue', label: 'Revenue' },
];

/**
 * `null` for a market with no financial report, regardless of `sortKey` - there
 * is nothing to rank it by, and it must sort last rather than tying with a
 * measured zero.
 */
export function marketSortValue(
  market: MarketWithFinancialReportEntity,
  sortKey: MarketSortKey,
): number | null {
  const report = market.financial_report;

  if (report == null) {
    return null;
  }

  switch (sortKey) {
    case 'fit':
      return investmentFit(market)?.score ?? null;
    case 'adr':
      return report.adr_cop;
    case 'occupancy':
      return report.occupancy_rate;
    case 'revenue':
      return report.annual_revenue_cop;
  }
}

/** Descending by `sortKey`, with report-less markets pushed to the end. */
export function sortMarkets(
  markets: readonly MarketWithFinancialReportEntity[],
  sortKey: MarketSortKey,
): MarketWithFinancialReportEntity[] {
  return [...markets].sort((a, b) => {
    const aValue = marketSortValue(a, sortKey);
    const bValue = marketSortValue(b, sortKey);

    if (aValue == null && bValue == null) {
      return 0;
    }
    if (aValue == null) {
      return 1;
    }
    if (bValue == null) {
      return -1;
    }

    return bValue - aValue;
  });
}
