import type { Meta, StoryObj } from '@storybook/react-vite';

import { AnchorLink } from './index';

const meta = {
  title: 'components/AnchorLink',
  component: AnchorLink,
  argTypes: {
    href: { control: 'text' },
    children: { control: 'text' },
  },
} as Meta<typeof AnchorLink>;

export default meta;
type Story = StoryObj<typeof AnchorLink>;

export const Default: Story = {
  args: {
    href: '#',
    children: 'Anchor Link',
  },
};
