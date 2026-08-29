import type { Meta, StoryObj } from '@storybook/react-vite';

import type { MarketWithFinancialReportEntity } from '@/types';
import { ColombiaMap } from './index';

const meta = {
  title: 'pages/markets/MarketsList/components/ColombiaMap',
  component: ColombiaMap,
} as Meta<typeof ColombiaMap>;

export default meta;
type Story = StoryObj<typeof ColombiaMap>;

function buildMarket(
  locality: string,
  latitude: number | null,
  longitude: number | null,
): MarketWithFinancialReportEntity {
  return {
    id: `${locality}-id`,
    created_at: '2026-07-29T01:46:56.335735Z',
    updated_at: '2026-08-20T02:06:09.952335Z',
    country: 'Colombia',
    district: null,
    locality,
    region: 'region',
    latitude,
    longitude,
    financial_report: null,
  };
}

export const Default: Story = {
  args: {
    markets: [
      buildMarket('Bogota', 4.6482, -74.0776),
      buildMarket('Calima', 3.9137, -76.4818),
      buildMarket('Pance', 3.3357, -76.5488),
      buildMarket('Salento', 4.6376, -75.5709),
      buildMarket('Santa Marta', null, null),
    ],
    onSelectMarket: () => {},
  },
};
