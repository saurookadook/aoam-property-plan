import type { Meta, StoryObj } from '@storybook/react-vite';
import {
  reactRouterParameters, // force formatting
  withRouter,
} from 'storybook-addon-remix-react-router';

import { StoryLayout } from '@/__storybook__/constants';
import { queryClient } from '@/app/browserRouter';
import { MarketsList, marketsListLoader } from './index';

const meta = {
  title: 'pages/markets/MarketsList',
  component: MarketsList,
  decorators: [withRouter],
  parameters: {
    layout: StoryLayout.centered,
    reactRouter: reactRouterParameters({
      routing: [
        {
          loader: marketsListLoader(queryClient),
          path: '/markets',
        },
      ],
    }),
  },
} as Meta<typeof MarketsList>;

export default meta;
type Story = StoryObj<typeof MarketsList>;

export const Default: Story = {};
