import type { Meta, StoryObj } from '@storybook/react-vite';

import { StoryLayout } from '@/__storybook__/constants';
import { queryClient } from '@/app/browserRouter';
import { Home } from './index';

const meta = {
  title: 'pages/Home',
  component: Home,
  parameters: {
    layout: StoryLayout.centered,
  },
} as Meta<typeof Home>;

export default meta;
type Story = StoryObj<typeof Home>;

export const FullData: Story = {};
