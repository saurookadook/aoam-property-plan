import type { PropertyAnalyzeRequest } from '@/types';

/**
 * `services/calculations.PropertyScenario`'s own defaults (`constants/colombia.py`),
 * mirrored here so a never-analysed property's `AssumptionsPanel` starts from the
 * same numbers the backend would apply if every field were omitted, rather than
 * from empty inputs the user has to fill in from scratch.
 */
export const DEFAULT_SCENARIO_OVERRIDES: PropertyAnalyzeRequest = {
  down_payment_percentage: 30.0,
  interest_rate_percentage: 10.0,
  loan_term_years: 15,
  management_fee_percentage: 22.0,
  maintenance_reserve_percentage: 1.0,
  closing_costs_percentage: 2.75,
  predial_rate_percentage: 0.8,
};
