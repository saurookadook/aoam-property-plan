import { useState } from 'react';
import type { Meta, StoryObj } from '@storybook/react-vite';

import { StoryLayout } from '@/__storybook__/constants';
import { PropertyLocationPicker } from './index';

const meta = {
  title: 'pages/properties/PropertyCreate/components/PropertyLocationPicker',
  component: PropertyLocationPicker,
  parameters: { layout: StoryLayout.padded },
} as Meta<typeof PropertyLocationPicker>;

export default meta;
type Story = StoryObj<typeof PropertyLocationPicker>;

export const Unset: Story = {
  args: { latitude: null, longitude: null, onPick: () => {} },
};

export const Picked: Story = {
  args: { latitude: 3.9151, longitude: -76.4802, onPick: () => {} },
};

export const Interactive: Story = {
  render: function Render() {
    const [position, setPosition] = useState<{ lat: number; lng: number } | null>(
      null,
    );

    return (
      <PropertyLocationPicker
        latitude={position?.lat ?? null}
        longitude={position?.lng ?? null}
        onPick={(lat, lng) => setPosition({ lat, lng })}
      />
    );
  },
};
