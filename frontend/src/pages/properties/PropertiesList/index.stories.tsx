import type { Meta, StoryObj } from '@storybook/react-vite';
import {
  reactRouterParameters, // force formatting
  withRouter,
} from 'storybook-addon-remix-react-router';

import { StoryLayout } from '@/__storybook__/constants';
import { queryClient } from '@/app/browserRouter';
import { PropertiesList, propertiesListLoader } from './index';

const meta = {
  title: 'pages/properties/PropertiesList',
  component: PropertiesList,
  decorators: [withRouter],
  parameters: {
    layout: StoryLayout.centered,
    reactRouter: reactRouterParameters({
      routing: [
        {
          loader: propertiesListLoader(queryClient),
          path: '/properties',
        },
      ],
    }),
  },
} as Meta<typeof PropertiesList>;

export default meta;
type Story = StoryObj<typeof PropertiesList>;

export const Default: Story = {};
