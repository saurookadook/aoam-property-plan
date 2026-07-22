import type { Meta, StoryObj } from '@storybook/react-vite';
import {
  reactRouterParameters, // force formatting
  withRouter,
} from 'storybook-addon-remix-react-router';

import { StoryLayout } from '@/__storybook__/constants';
import { queryClient } from '@/app/browserRouter';
import { ListingOverview, listingOverviewLoader } from './index';

const meta = {
  title: 'pages/listings/ListingOverview',
  component: ListingOverview,
  decorators: [withRouter],
  parameters: {
    layout: StoryLayout.centered,
    reactRouter: reactRouterParameters({
      routing: [
        {
          loader: listingOverviewLoader(queryClient),
          path: '/listings/:listingId',
        },
      ],
    }),
  },
} as Meta<typeof ListingOverview>;

export default meta;
type Story = StoryObj<typeof ListingOverview>;

export const CalimaTreehouse: Story = {
  parameters: {
    reactRouter: reactRouterParameters({
      location: {
        pathParams: { listingId: '2d5175ef-d2e1-42e5-ad06-b5d5518f7964' },
      },
    }),
  },
};

export const CalimaLakeNirvana: Story = {
  parameters: {
    reactRouter: reactRouterParameters({
      location: {
        pathParams: { listingId: '0fa060df-d145-4fcf-91ad-d0d2501562ad' },
      },
    }),
  },
};

export const CalimaEntireHomeNoName: Story = {
  parameters: {
    reactRouter: reactRouterParameters({
      location: {
        pathParams: { listingId: 'b7a0dbab-192f-4731-9ad4-5700216ea82f' },
      },
    }),
  },
};
