import type { PropertyAnalyzeRequest, PropertyFinancialReportEntity } from '@/types';

/**
 * Report column -> scenario field, for every assumption a re-analysis can carry.
 *
 * Written out rather than derived, because the one pair that differs is the one
 * that matters: `property_financial_reports` stores the rate in a column called
 * `interest_rate`, and the scenario field is `interest_rate_percentage`. Seeding
 * a form from a stored report and posting it straight back sends the column
 * name. Before `extra="forbid"` landed that was a **silent wrong number** - the
 * key was ignored, `overrides()` omitted it, and `PropertyScenario` applied its
 * 10% default, so a user who set 14% got a figure computed at 10%.
 *
 * The backend now 422s on it, which makes the bug loud. This map is what stops
 * it happening at all, and `_tests/propertyAnalysis.test.ts` asserts the pair
 * directly so a rename on either side fails here rather than in production.
 *
 * `annual_revenue_cop` and `cop_per_usd` are absent on purpose: the analysis
 * derives both, and `PropertyAnalyzeRequest` forbids them.
 */
export const REPORT_COLUMN_TO_SCENARIO_FIELD = {
  purchase_price_cop: 'purchase_price_cop',
  assessed_value_cop: 'assessed_value_cop',
  hoa_monthly_cop: 'hoa_monthly_cop',
  renovation_budget_cop: 'renovation_budget_cop',
  down_payment_percentage: 'down_payment_percentage',
  interest_rate: 'interest_rate_percentage',
  loan_term_years: 'loan_term_years',
  management_fee_percentage: 'management_fee_percentage',
  maintenance_reserve_percentage: 'maintenance_reserve_percentage',
  closing_costs_percentage: 'closing_costs_percentage',
  predial_rate_percentage: 'predial_rate_percentage',
} as const satisfies Partial<
  Record<keyof PropertyFinancialReportEntity, keyof PropertyAnalyzeRequest>
>;

/**
 * The assumptions a stored report was run under, as a request body.
 *
 * A `null` column is **dropped rather than defaulted**, mirroring
 * `services/property_analysis.scenario_from_report`: omitting it lets
 * `PropertyScenario` re-apply the same Colombia default the original run used,
 * whereas sending an invented `0` would quietly change the arithmetic.
 */
export function reportToScenarioOverrides(
  report: Pick<
    PropertyFinancialReportEntity,
    keyof typeof REPORT_COLUMN_TO_SCENARIO_FIELD
  >,
): PropertyAnalyzeRequest {
  const overrides: PropertyAnalyzeRequest = {};

  for (const [column, field] of Object.entries(REPORT_COLUMN_TO_SCENARIO_FIELD)) {
    const value = report[column as keyof typeof REPORT_COLUMN_TO_SCENARIO_FIELD];

    if (value == null || !Number.isFinite(value)) {
      continue;
    }

    overrides[field] = value;
  }

  return overrides;
}
