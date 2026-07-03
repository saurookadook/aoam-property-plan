import type { Meta, StoryObj } from '@storybook/react-vite';

import { MarketsList } from './index';

const meta = {
  title: 'pages/markets/MarketsList',
  component: MarketsList,
} as Meta<typeof MarketsList>;

export default meta;
type Story = StoryObj<typeof MarketsList>;

export const Default: Story = {};
