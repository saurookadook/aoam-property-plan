import type { Meta, StoryObj } from '@storybook/react-vite';

import { StoryLayout } from '@/__storybook__/constants';
import { ExpenseBreakdownCard } from './index';

const meta = {
  title: 'pages/properties/PropertyOverview/components/ExpenseBreakdownCard',
  component: ExpenseBreakdownCard,
  parameters: { layout: StoryLayout.padded },
} as Meta<typeof ExpenseBreakdownCard>;

export default meta;
type Story = StoryObj<typeof ExpenseBreakdownCard>;

export const CopOnly: Story = {
  args: {
    expenses: {
      mortgage_cop: 1900000,
      hoa_cop: 0,
      management_fee_cop: 121000,
      maintenance_reserve_cop: 27500,
      predial_cop: 56666,
      total_cop: 2105166,
    },
    rate: null,
  },
};

export const WithReportRate: Story = {
  args: {
    ...CopOnly.args,
    rate: { rate: 4013, rateAsOf: '2026-08-20', rateSource: 'report' },
  },
};
