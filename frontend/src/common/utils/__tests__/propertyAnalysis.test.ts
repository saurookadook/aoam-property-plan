import { describe, expect, it } from 'vitest';

import type { PropertyFinancialReportEntity } from '@/types';
import {
  REPORT_COLUMN_TO_SCENARIO_FIELD,
  reportToScenarioOverrides,
} from '../propertyAnalysis';

const REPORT: Pick<
  PropertyFinancialReportEntity,
  keyof typeof REPORT_COLUMN_TO_SCENARIO_FIELD
> = {
  purchase_price_cop: 850_000_000,
  assessed_value_cop: 850_000_000,
  hoa_monthly_cop: 0,
  renovation_budget_cop: 0,
  down_payment_percentage: 30,
  interest_rate: 14,
  loan_term_years: 15,
  management_fee_percentage: 22,
  maintenance_reserve_percentage: 1,
  closing_costs_percentage: 2.75,
  predial_rate_percentage: 0.8,
};

describe('reportToScenarioOverrides', () => {
  it('maps `interest_rate` to `interest_rate_percentage`', () => {
    // The whole reason this module exists. The report column and the scenario
    // field have different names; posting the column name back used to be
    // ignored, so a user who set 14% silently got a figure computed at the 10%
    // default. It is now a 422 - and this mapping stops it reaching the server.
    const overrides = reportToScenarioOverrides(REPORT);

    expect(overrides.interest_rate_percentage).toBe(14);
    expect(overrides).not.toHaveProperty('interest_rate');
  });

  it('carries every other assumption across unchanged', () => {
    expect(reportToScenarioOverrides(REPORT)).toEqual({
      purchase_price_cop: 850_000_000,
      assessed_value_cop: 850_000_000,
      hoa_monthly_cop: 0,
      renovation_budget_cop: 0,
      down_payment_percentage: 30,
      interest_rate_percentage: 14,
      loan_term_years: 15,
      management_fee_percentage: 22,
      maintenance_reserve_percentage: 1,
      closing_costs_percentage: 2.75,
      predial_rate_percentage: 0.8,
    });
  });

  it('keeps an explicit zero rather than treating it as absent', () => {
    // `hoa_monthly_cop: 0` is a real assumption - a property with no HOA - and
    // dropping it would fall back to the city default.
    expect(reportToScenarioOverrides({ ...REPORT, hoa_monthly_cop: 0 })).toHaveProperty(
      'hoa_monthly_cop',
      0,
    );
  });

  it('drops a null column instead of defaulting it', () => {
    // Mirrors `scenario_from_report`: omitting the key lets `PropertyScenario`
    // re-apply the same Colombia default the original run used, whereas sending
    // an invented `0` would quietly change the arithmetic.
    const overrides = reportToScenarioOverrides({
      ...REPORT,
      interest_rate: null,
      loan_term_years: null,
    });

    expect(overrides).not.toHaveProperty('interest_rate_percentage');
    expect(overrides).not.toHaveProperty('loan_term_years');
  });

  it('sends no key the analyze request forbids', () => {
    // `PropertyAnalyzeRequest` is `extra="forbid"`, so any key outside the
    // scenario's own fields is a 422 for the whole request.
    const forbidden = ['annual_revenue_cop', 'cop_per_usd', 'interest_rate'];
    const overrides = reportToScenarioOverrides(REPORT);

    forbidden.forEach((key) => expect(overrides).not.toHaveProperty(key));
  });
});
