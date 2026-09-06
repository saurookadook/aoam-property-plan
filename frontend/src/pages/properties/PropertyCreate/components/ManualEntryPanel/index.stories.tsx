import { useState } from 'react';
import type { Meta, StoryObj } from '@storybook/react-vite';

import { StoryLayout } from '@/__storybook__/constants';
import { EMPTY_MANUAL_ENTRY_VALUES } from '../../utils';
import { ManualEntryPanel } from './index';

const meta = {
  title: 'pages/properties/PropertyCreate/components/ManualEntryPanel',
  component: ManualEntryPanel,
  parameters: { layout: StoryLayout.padded },
} as Meta<typeof ManualEntryPanel>;

export default meta;
type Story = StoryObj<typeof ManualEntryPanel>;

export const Empty: Story = {
  args: { values: EMPTY_MANUAL_ENTRY_VALUES, onChange: () => {} },
};

export const Interactive: Story = {
  render: function Render() {
    const [values, setValues] = useState(EMPTY_MANUAL_ENTRY_VALUES);
    return <ManualEntryPanel values={values} onChange={setValues} />;
  },
};
