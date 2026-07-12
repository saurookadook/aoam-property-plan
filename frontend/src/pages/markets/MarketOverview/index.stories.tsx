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
        pathParams: { marketId: '02f7996b-7111-48c0-beb9-c4fe14986859' },
      },
    }),
  },
};

export const Salento: Story = {
  parameters: {
    reactRouter: reactRouterParameters({
      location: {
        pathParams: { marketId: 'f68ec319-eab2-40d9-949e-c4d1eda49544' },
      },
    }),
  },
};
