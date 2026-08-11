import type { Meta, StoryObj } from '@storybook/react-vite';

import { StoryLayout } from '@/__storybook__/constants';
import { FlexColumn } from '@/layouts';
import { ListingCarouselCard } from './index';

const meta = {
  title: 'pages/home/ListingCarouselCard',
  component: ListingCarouselCard,
  decorators: [
    (Story) => {
      return (
        <FlexColumn style={{ maxWidth: '45vw' }}>
          <Story />
        </FlexColumn>
      );
    },
  ],
  parameters: {
    layout: StoryLayout.centered,
  },
} as Meta<typeof ListingCarouselCard>;

export default meta;
type Story = StoryObj<typeof ListingCarouselCard>;

const highestEarnerListing = {
  created_at: '2026-06-26T06:00:02.042731Z',
  updated_at: '2026-06-26T06:00:02.042731Z',
  id: '1bc5fd77-b7a6-4055-812c-dfc49c246b9e',
  cover_photo_url:
    'https://a0.muscache.com/im/pictures/airflow/Hosting-779010768604893929/original/7bd4ace6-45d3-4228-bb2b-5f65676555b5.jpg',
  market_id: 'f68ec319-eab2-40d9-949e-c4d1eda49544',
  name: 'House in the mountains near Salento main park',
  ttm_revenue: 169204065,
  country: 'Colombia',
  locality: 'Salento',
  region: 'Quindío',
};

export const HighestEarnerListing: Story = {
  args: {
    listing: {
      ...highestEarnerListing,
    },
  },
};

export const HighestEarnerListingNoCoverPhoto: Story = {
  args: {
    listing: {
      ...highestEarnerListing,
      cover_photo_url: undefined,
    },
  },
};

export const NewestListing: Story = {
  args: {
    listing: {
      created_at: '2026-06-26T06:00:02.108079Z',
      updated_at: '2026-06-26T06:00:02.108079Z',
      id: '7c6025b6-0b72-4973-9277-d240d7efdc72',
      cover_photo_url:
        'https://a0.muscache.com/im/pictures/2956e942-6be2-49a1-bfd0-387aa27a21d1.jpg',
      market_id: 'f68ec319-eab2-40d9-949e-c4d1eda49544',
      name: 'Las Margaritas, Salento',
    },
  },
};
