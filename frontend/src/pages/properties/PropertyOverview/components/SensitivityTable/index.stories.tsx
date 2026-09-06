import type { Meta, StoryObj } from '@storybook/react-vite';

import { StoryLayout } from '@/__storybook__/constants';
import { SensitivityTable } from './index';

const meta = {
  title: 'pages/properties/PropertyOverview/components/SensitivityTable',
  component: SensitivityTable,
  parameters: { layout: StoryLayout.padded },
} as Meta<typeof SensitivityTable>;

export default meta;
type Story = StoryObj<typeof SensitivityTable>;

export const Default: Story = {
  args: {
    cells: [
      { revenue_factor: 0.9, annual_revenue_cop: 21762000, coc_return_percentage: -24.7, payback_years: null },
      { revenue_factor: 1.0, annual_revenue_cop: 24180000, coc_return_percentage: -23.8, payback_years: null },
      { revenue_factor: 1.1, annual_revenue_cop: 26598000, coc_return_percentage: -22.8, payback_years: null },
    ],
    rate: null,
  },
};
