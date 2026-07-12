import type { Meta, StoryObj } from '@storybook/react-vite';

import { MarketOverview } from './index';

const meta = {
  title: 'pages/markets/MarketOverview',
  component: MarketOverview,
} as Meta<typeof MarketOverview>;

export default meta;
type Story = StoryObj<typeof MarketOverview>;

export const Salento: Story = {
  parameters: {
    reactRouter: {
      routePath: '/markets/:marketId',
      routeParams: { marketId: 'f68ec319-eab2-40d9-949e-c4d1eda49544' },
    },
  },
};
