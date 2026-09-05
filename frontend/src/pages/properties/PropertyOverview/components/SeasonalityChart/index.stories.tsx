import type { Meta, StoryObj } from '@storybook/react-vite';

import { StoryLayout } from '@/__storybook__/constants';
import { SeasonalityChart } from './index';

const meta = {
  title: 'pages/properties/PropertyOverview/components/SeasonalityChart',
  component: SeasonalityChart,
  parameters: { layout: StoryLayout.padded },
} as Meta<typeof SeasonalityChart>;

export default meta;
type Story = StoryObj<typeof SeasonalityChart>;

export const Calima: Story = {
  args: {
    distribution: [
      0.1042, 0.0788, 0.0796, 0.0731, 0.0724, 0.0869, 0.1058, 0.0913, 0.0702, 0.0714,
      0.0716, 0.0947,
    ],
  },
};

export const NotYetAvailable: Story = {
  args: { distribution: null },
};
