import { useState } from 'react';
import type { Meta, StoryObj } from '@storybook/react-vite';

import type { MarketSortKey } from '../../utils/sortMarkets';
import { MarketSortControls } from './index';

const meta = {
  title: 'pages/markets/MarketsList/components/MarketSortControls',
  component: MarketSortControls,
} as Meta<typeof MarketSortControls>;

export default meta;
type Story = StoryObj<typeof MarketSortControls>;

export const Default: Story = {
  args: { sortKey: 'fit', onSortKeyChange: () => {} },
  render: (args) => {
    function Interactive() {
      const [sortKey, setSortKey] = useState<MarketSortKey>(args.sortKey);

      return <MarketSortControls sortKey={sortKey} onSortKeyChange={setSortKey} />;
    }

    return <Interactive />;
  },
};
