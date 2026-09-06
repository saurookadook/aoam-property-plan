import type { Meta, StoryObj } from '@storybook/react-vite';

import { StoryLayout } from '@/__storybook__/constants';
import { PropertyCreate } from './index';

const meta = {
  title: 'pages/properties/PropertyCreate',
  component: PropertyCreate,
  parameters: { layout: StoryLayout.centered },
} as Meta<typeof PropertyCreate>;

export default meta;
type Story = StoryObj<typeof PropertyCreate>;

export const Default: Story = {};
