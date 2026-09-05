import type { Meta, StoryObj } from '@storybook/react-vite';

import { StoryLayout } from '@/__storybook__/constants';
import { DataConfidenceBanner } from './index';

const meta = {
  title: 'pages/properties/PropertyOverview/components/DataConfidenceBanner',
  component: DataConfidenceBanner,
  parameters: { layout: StoryLayout.padded },
} as Meta<typeof DataConfidenceBanner>;

export default meta;
type Story = StoryObj<typeof DataConfidenceBanner>;

export const Good: Story = {
  args: { source: 'comp_derived', compCount: 12 },
};

export const Fair: Story = {
  args: { source: 'comp_derived', compCount: 6 },
};

export const ThinComps: Story = {
  args: { source: 'airroi_p25_thin_comps', compCount: 1 },
};

export const NotAnalysed: Story = {
  args: { source: null, compCount: null },
};
