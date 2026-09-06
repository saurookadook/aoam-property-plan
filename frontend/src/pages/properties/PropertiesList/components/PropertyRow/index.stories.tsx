import type { Meta, StoryObj } from '@storybook/react-vite';

import { StoryLayout } from '@/__storybook__/constants';
import type { PropertyEntity } from '@/types';
import { PropertyRow } from './index';

const baseProperty: PropertyEntity = {
  id: '8f2d6b04-7e19-4a35-8c60-d3b5194ae872',
  created_at: '2026-07-29T01:46:56.335735Z',
  updated_at: '2026-08-20T02:06:09.952335Z',
  address: 'Km 8 Via Darien 3-15',
  amenities: ['Wifi', 'Kitchen', 'Free parking', 'Pool'],
  baths: 1.5,
  bedrooms: 2,
  city: 'Calima',
  country: 'Colombia',
  description: 'Casa Lago Calima - 2 bedroom Calima property.',
  guests: 4,
  latitude: 3.9151,
  longitude: -76.4802,
  market_id: '7e1960b2-a442-410d-96ba-d302e3ad684b',
  name: 'Casa Lago Calima',
  neighborhood: 'Darién',
  notes: null,
  postal_code: null,
  property_type: 'House',
  purchase_price_cop: 620000000,
  purchase_price_usd: 154497.88,
  source_created_at: '2026-07-29T01:46:56.335735Z',
  source_url: 'https://www.fincaraiz.com.co/inmueble/casa-lago-calima',
  state: 'Valle del Cauca',
  status: 'active',
};

const meta = {
  title: 'pages/properties/PropertiesList/components/PropertyRow',
  component: PropertyRow,
  parameters: { layout: StoryLayout.padded },
} as Meta<typeof PropertyRow>;

export default meta;
type Story = StoryObj<typeof PropertyRow>;

export const CopOnly: Story = {
  args: { property: baseProperty, rate: null },
};

export const WithLiveRate: Story = {
  args: {
    property: baseProperty,
    rate: { rate: 4013, rateAsOf: '2026-08-20', rateSource: 'live' },
  },
};

export const Unnamed: Story = {
  args: { property: { ...baseProperty, name: null }, rate: null },
};
