import type { Meta, StoryObj } from '@storybook/react-vite';

import { StoryLayout } from '@/__storybook__/constants';
import type { PropertyCompWithListingEntity } from '@/types';
import { PropertyCompsTable } from './index';

const comp: PropertyCompWithListingEntity = {
  id: '322851e7-f8bc-5bd5-a326-706312954ae0',
  created_at: '2026-08-20T02:06:09.952335Z',
  updated_at: '2026-08-20T02:06:09.952335Z',
  adr_cop: 1842000,
  captured_at: '2026-08-20T02:06:09.952335Z',
  distance_km: 3.18,
  listing_id: '58d212b6-0cd9-593e-a5aa-91102feb6611',
  occupancy_rate: 0.208,
  property_id: '8f2d6b04-7e19-4a35-8c60-d3b5194ae872',
  ttm_revenue_cop: 139844640,
  ttm_total_days: 365,
  listing: {
    id: '58d212b6-0cd9-593e-a5aa-91102feb6611',
    airroi_id: 41000001,
    baths: 5.5,
    bedrooms: 5,
    cover_photo_url: 'https://a0.muscache.com/im/pictures/aoam-comp-1.jpg',
    latitude: 4.6399,
    longitude: -75.5711,
    name: 'Villa Lago Calima (16 guests)',
    property_type: 'Entire home',
    source_url: 'https://www.airbnb.com/rooms/41000001',
  },
};

const meta = {
  title: 'pages/properties/PropertyOverview/components/PropertyCompsTable',
  component: PropertyCompsTable,
  parameters: { layout: StoryLayout.padded },
} as Meta<typeof PropertyCompsTable>;

export default meta;
type Story = StoryObj<typeof PropertyCompsTable>;

export const OneComp: Story = {
  args: {
    comps: [comp],
    propertyId: '8f2d6b04-7e19-4a35-8c60-d3b5194ae872',
    rate: null,
  },
};

export const Empty: Story = {
  args: {
    comps: [],
    propertyId: '8f2d6b04-7e19-4a35-8c60-d3b5194ae872',
    rate: null,
  },
};
