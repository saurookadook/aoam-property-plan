import type { Meta, StoryObj } from '@storybook/react-vite';

import type { MarketWithFinancialReportEntity } from '@/types';
import { CurrencyProvider } from '@/providers';
import { MarketCard } from './index';

const meta = {
  title: 'pages/markets/MarketsList/components/MarketCard',
  component: MarketCard,
  decorators: [
    (Story) => (
      <CurrencyProvider>
        <Story />
      </CurrencyProvider>
    ),
  ],
} as Meta<typeof MarketCard>;

export default meta;
type Story = StoryObj<typeof MarketCard>;

const calima: MarketWithFinancialReportEntity = {
  id: '7e1960b2-a442-410d-96ba-d302e3ad684b',
  created_at: '2026-07-29T01:46:56.335735Z',
  updated_at: '2026-08-20T02:06:09.952335Z',
  country: 'Colombia',
  district: null,
  locality: 'Calima',
  region: 'Valle del Cauca',
  latitude: 3.9137,
  longitude: -76.4818,
  financial_report: {
    id: '0c3aaed1-13b1-53fc-bd05-f9e4a59d89c8',
    created_at: '2026-07-29T01:46:56.335735Z',
    updated_at: '2026-08-20T02:06:09.952335Z',
    market_id: '7e1960b2-a442-410d-96ba-d302e3ad684b',
    adr_cop: 857_200,
    adr_usd: null,
    annual_revenue_cop: 31_680_000,
    annual_revenue_usd: null,
    last_updated: '2026-08-20T02:06:09.952335Z',
    listing_count: 178.3,
    monthly_revenue_distribution: null,
    occupancy_rate: 0.182,
    peak_months: ['January', 'June', 'December'],
  },
};

const santaMarta: MarketWithFinancialReportEntity = {
  id: 'b2f1c0a2-3d6e-4a71-9c48-2ef0a6d51b99',
  created_at: '2026-07-29T01:46:56.335735Z',
  updated_at: '2026-08-20T02:06:09.952335Z',
  country: 'Colombia',
  district: null,
  locality: 'Santa Marta',
  region: 'Magdalena',
  latitude: null,
  longitude: null,
  financial_report: null,
};

export const WithReport: Story = {
  args: {
    budgetCop: 1_766_000_000,
    market: calima,
    purchasePricesCop: [620_000_000, 700_000_000, 550_000_000],
    rate: { rate: 4013, rateAsOf: '2026-08-20', rateSource: 'live' },
  },
};

export const NoReportYet: Story = {
  args: {
    budgetCop: 1_766_000_000,
    market: santaMarta,
    purchasePricesCop: [],
    rate: { rate: 4013, rateAsOf: '2026-08-20', rateSource: 'live' },
  },
};

export const Selected: Story = {
  args: {
    ...WithReport.args,
    isSelected: true,
  },
};
