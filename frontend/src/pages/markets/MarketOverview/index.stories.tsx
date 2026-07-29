import type { Meta, StoryObj } from '@storybook/react-vite';
import {
  reactRouterParameters, // force formatting
  withRouter,
} from 'storybook-addon-remix-react-router';

import { StoryLayout } from '@/__storybook__/constants';
import { queryClient } from '@/app/browserRouter';
import { MarketOverview, marketOverviewLoader } from './index';

const meta = {
  title: 'pages/markets/MarketOverview',
  component: MarketOverview,
  decorators: [withRouter],
  parameters: {
    layout: StoryLayout.centered,
    reactRouter: reactRouterParameters({
      routing: [
        {
          loader: marketOverviewLoader(queryClient),
          path: '/markets/:marketId',
        },
      ],
    }),
  },
} as Meta<typeof MarketOverview>;

export default meta;
type Story = StoryObj<typeof MarketOverview>;

export const Calima: Story = {
  parameters: {
    reactRouter: reactRouterParameters({
      location: {
        pathParams: { marketId: '7e1960b2-a442-410d-96ba-d302e3ad684b' },
      },
    }),
  },
};

export const Pance: Story = {
  parameters: {
    reactRouter: reactRouterParameters({
      location: {
        pathParams: { marketId: '45841a54-2ee0-4736-9b78-8e9b34f4a1eb' },
      },
    }),
  },
};

export const Salento: Story = {
  parameters: {
    reactRouter: reactRouterParameters({
      location: {
        pathParams: { marketId: '63413e5b-db94-419a-bd74-033d35f9ece8' },
      },
    }),
  },
};
