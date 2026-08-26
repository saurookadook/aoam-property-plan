import type { BaseEntity } from './entity';
import type { PropertyCompWithListingEntity } from './comps';

/**
 * Which estimate `annual_revenue_cop` was taken from.
 *
 * The `_thin_comps` variants are the ones the confidence UI exists for: AirROI's
 * own model with too few surviving comparables to corroborate it.
 */
export type AnnualRevenueSource =
  | 'airroi_p25'
  | 'airroi_avg'
  | 'comp_derived'
  | 'airroi_p25_thin_comps'
  | 'airroi_avg_thin_comps';

/** Mirrors `models/property_financial_report/entity.PropertyFinancialReportEntity`. */
export type PropertyFinancialReportEntity = BaseEntity & {
  property_id: string;
  airroi_adr_cop: number | null;
  airroi_occupancy_rate: number | null;
  /** AirROI's own annual estimate - a mean over a right-skewed distribution. */
  airroi_revenue_cop: number | null;
  airroi_revenue_p25_cop: number | null;
  airroi_revenue_p50_cop: number | null;
  airroi_revenue_p75_cop: number | null;
  airroi_revenue_p90_cop: number | null;
  annual_net_income_cop: number | null;
  annual_net_income_usd: number | null;
  annual_revenue_cop: number | null;
  annual_revenue_source: AnnualRevenueSource | null;
  annual_revenue_usd: number | null;
  /** Cadastral (avaluo catastral) value predial is levied on. */
  assessed_value_cop: number | null;
  calculated_at: string | null;
  cash_invested_cop: number | null;
  cash_invested_usd: number | null;
  closing_costs_percentage: number | null;
  coc_return_percentage: number | null;
  comp_count: number | null;
  comp_derived_revenue_cop: number | null;
  down_payment_percentage: number | null;
  /** The COP-per-USD rate every `_usd` column on this row was computed with. */
  exchange_rate: number | null;
  hoa_monthly_cop: number | null;
  /**
   * @note The column is `interest_rate`; the scenario field is
   * `interest_rate_percentage`. Only `reportToScenarioOverrides` bridges them.
   */
  interest_rate: number | null;
  loan_term_years: number | null;
  maintenance_reserve_percentage: number | null;
  management_fee_percentage: number | null;
  monthly_expenses_cop: number | null;
  monthly_expenses_usd: number | null;
  monthly_mortgage_cop: number | null;
  /** Twelve fractions summing to 1.0 - the only seasonality AirROI exposes. */
  monthly_revenue_distribution: number[] | null;
  payback_years: number | null;
  /** Full English month names. */
  peak_months: string[] | null;
  predial_rate_percentage: number | null;
  purchase_price_cop: number | null;
  renovation_budget_cop: number | null;
};

/** Mirrors `services/calculations.MonthlyExpenseBreakdown`. */
export type MonthlyExpenseBreakdown = {
  mortgage_cop: number;
  hoa_cop: number;
  management_fee_cop: number;
  maintenance_reserve_cop: number;
  predial_cop: number;
  /** A pydantic `computed_field`, so it is served but never sent. */
  total_cop: number;
};

/** Mirrors `services/calculations.SensitivityCell`. */
export type SensitivityCell = {
  revenue_factor: number;
  annual_revenue_cop: number;
  coc_return_percentage: number;
  payback_years: number | null;
};

/** Mirrors `api/models/property_analysis.PropertyAnalysisData`. */
export type PropertyAnalysisData = {
  report: PropertyFinancialReportEntity;
  expenses: MonthlyExpenseBreakdown;
  sensitivity: SensitivityCell[];
};

/**
 * Mirrors the generated `PropertyAnalyzeRequest`, whose fields are every
 * `PropertyScenario` knob except the two the analysis derives
 * (`annual_revenue_cop`, `cop_per_usd`).
 *
 * The model is `extra="forbid"`, so an unrecognised key - `interest_rate`, say -
 * is a 422 rather than a silent fallback to the Colombia default.
 */
export type PropertyAnalyzeRequest = {
  purchase_price_cop?: number;
  assessed_value_cop?: number;
  hoa_monthly_cop?: number;
  renovation_budget_cop?: number;
  down_payment_percentage?: number;
  interest_rate_percentage?: number;
  loan_term_years?: number;
  management_fee_percentage?: number;
  maintenance_reserve_percentage?: number;
  closing_costs_percentage?: number;
  predial_rate_percentage?: number;
};

export type PropertyCompsData = PropertyCompWithListingEntity[];
