import type { Meta, StoryObj } from '@storybook/react-vite';

import { LoadingState } from './index';

const meta = {
  title: 'components/LoadingState',
  component: LoadingState,
  argTypes: {
    children: { control: 'text' },
  },
} as Meta<typeof LoadingState>;

export default meta;
type Story = StoryObj<typeof LoadingState>;

export const Default: Story = {};

export const WithChildText: Story = {
  args: {
    children: 'Loading State',
  },
};
