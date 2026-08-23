import type { BaseEntity } from './entity';

/**
 * `district` is `Optional[str]` on `MarketEntity`, so it is `string | null` and
 * not `string?` - the API sends an explicit `null`.
 */
export type MarketEntity = BaseEntity & {
  country: string;
  district: string | null;
  locality: string;
  region: string;
};

/** Mirrors `models/market_financial_report/entity.MarketFinancialReportEntity`. */
export type MarketFinancialReportEntity = BaseEntity & {
  market_id: string;
  adr_cop: number;
  adr_usd: number | null;
  annual_revenue_cop: number;
  annual_revenue_usd: number | null;
  last_updated: string;
  /**
   * A 12-month average, so a float. Round it for display - `6375.8` active
   * listings reads as a bug.
   */
  listing_count: number;
  monthly_revenue_distribution: number[] | null;
  occupancy_rate: number;
  peak_months: string[] | null;
};

/**
 * Mirrors `models/market/entity.MarketWithFinancialReportEntity`, which
 * `GET /api/markets` serves.
 *
 * `latitude`/`longitude` are the centroid of the market's ingested listings and
 * are `null` for a market with nothing ingested; `financial_report` is `null`
 * for a market never summarised. Both are ordinary states of a fresh roster.
 */
export type MarketWithFinancialReportEntity = MarketEntity & {
  financial_report: MarketFinancialReportEntity | null;
  latitude: number | null;
  longitude: number | null;
};
