import type { Meta, StoryObj } from '@storybook/react-vite';

import { StoryLayout } from '@/__storybook__/constants';
import type { PropertyFinancialReportEntity } from '@/types';
import { RevenueComparisonRow } from './index';

const baseReport = {
  id: 'c3e91a48-5f27-4d06-8b93-2a71046ed5b8',
  created_at: '2026-08-20T02:06:09.952335Z',
  updated_at: '2026-08-20T02:06:09.952335Z',
  property_id: '3a1c8f52-0d47-4e69-9b83-5c2a7e1d40f6',
  airroi_adr_cop: 700000,
  airroi_occupancy_rate: 0.34,
  airroi_revenue_cop: 40000000,
  airroi_revenue_p25_cop: 24000000,
  airroi_revenue_p50_cop: 33000000,
  airroi_revenue_p75_cop: 45000000,
  airroi_revenue_p90_cop: 60000000,
  annual_net_income_cop: 8000000,
  annual_net_income_usd: 1994,
  annual_revenue_cop: 33000000,
  annual_revenue_source: 'comp_derived',
  annual_revenue_usd: 8225,
  assessed_value_cop: 850000000,
  calculated_at: '2026-08-20T02:06:09.952335Z',
  cash_invested_cop: 280000000,
  cash_invested_usd: 69773,
  closing_costs_percentage: 2.75,
  coc_return_percentage: 9.4,
  comp_count: 12,
  comp_derived_revenue_cop: 33000000,
  down_payment_percentage: 30,
  exchange_rate: 4013,
  hoa_monthly_cop: 0,
  interest_rate: 10,
  loan_term_years: 15,
  maintenance_reserve_percentage: 1,
  management_fee_percentage: 22,
  monthly_expenses_cop: 2100000,
  monthly_expenses_usd: 523,
  monthly_mortgage_cop: 1900000,
  monthly_revenue_distribution: null,
  payback_years: 10.6,
  peak_months: ['January', 'June', 'December'],
  predial_rate_percentage: 0.8,
  purchase_price_cop: 850000000,
  renovation_budget_cop: 0,
} satisfies PropertyFinancialReportEntity;

const meta = {
  title: 'pages/properties/PropertyOverview/components/RevenueComparisonRow',
  component: RevenueComparisonRow,
  parameters: { layout: StoryLayout.padded },
} as Meta<typeof RevenueComparisonRow>;

export default meta;
type Story = StoryObj<typeof RevenueComparisonRow>;

export const CompDerivedWins: Story = {
  args: { report: baseReport },
};

export const ThinComps: Story = {
  args: {
    report: {
      ...baseReport,
      annual_revenue_source: 'airroi_p25_thin_comps',
      annual_revenue_cop: 24000000,
      comp_derived_revenue_cop: null,
      comp_count: 1,
    },
  },
};
