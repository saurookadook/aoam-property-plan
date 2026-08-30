import type { Meta, StoryObj } from '@storybook/react-vite';

import { BudgetIndicator } from './index';

const meta = {
  title: 'pages/markets/MarketsList/components/MarketCard/BudgetIndicator',
  component: BudgetIndicator,
} as Meta<typeof BudgetIndicator>;

export default meta;
type Story = StoryObj<typeof BudgetIndicator>;

export const EnoughData: Story = {
  args: {
    budgetCop: 1_766_000_000,
    purchasePricesCop: [850_000_000, 1_120_000_000, 690_000_000],
  },
};

export const NotEnoughData: Story = {
  args: {
    budgetCop: 1_766_000_000,
    purchasePricesCop: [620_000_000, null],
  },
};

export const NoData: Story = {
  args: { budgetCop: 1_766_000_000, purchasePricesCop: [] },
};
