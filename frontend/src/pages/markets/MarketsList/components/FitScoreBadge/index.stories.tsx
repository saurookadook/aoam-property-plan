import type { Meta, StoryObj } from '@storybook/react-vite';

import { FitScoreBadge } from './index';

const meta = {
  title: 'pages/markets/MarketsList/components/FitScoreBadge',
  component: FitScoreBadge,
} as Meta<typeof FitScoreBadge>;

export default meta;
type Story = StoryObj<typeof FitScoreBadge>;

export const Pending: Story = {
  args: { fit: null },
};

export const Scored: Story = {
  args: {
    fit: {
      score: 45,
      isThinMarket: false,
      listingCount: 178.3,
      components: { revenue: 0.41, occupancy: 0.08, adr: 0.97, depth: 0.76 },
    },
  },
};

export const ThinMarket: Story = {
  args: {
    fit: {
      score: 47,
      isThinMarket: true,
      listingCount: 27.8,
      components: { revenue: 0.33, occupancy: 0.45, adr: 0.37, depth: 1.0 },
    },
  },
};
