import type { Meta, StoryObj } from '@storybook/react-vite';
import {
  reactRouterParameters, // force formatting
  withRouter,
} from 'storybook-addon-remix-react-router';

import { StoryLayout } from '@/__storybook__/constants';
import { queryClient } from '@/app/browserRouter';
import { PropertyOverview, propertyOverviewLoader } from './index';

const meta = {
  title: 'pages/properties/PropertyOverview',
  component: PropertyOverview,
  decorators: [withRouter],
  parameters: {
    layout: StoryLayout.centered,
    reactRouter: reactRouterParameters({
      routing: [
        {
          loader: propertyOverviewLoader(queryClient),
          path: '/properties/:propertyId',
        },
      ],
      location: { path: '/properties/8f2d6b04-7e19-4a35-8c60-d3b5194ae872' },
    }),
  },
} as Meta<typeof PropertyOverview>;

export default meta;
type Story = StoryObj<typeof PropertyOverview>;

export const ThinComps: Story = {};

export const NeverAnalysed: Story = {
  parameters: {
    reactRouter: reactRouterParameters({
      routing: [
        {
          loader: propertyOverviewLoader(queryClient),
          path: '/properties/:propertyId',
        },
      ],
      location: { path: '/properties/2e8a5f13-6d90-4c47-8b25-71c3e9d0a4f8' },
    }),
  },
};
