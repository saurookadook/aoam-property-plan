import { afterEach, describe, expect, it } from 'vitest';
import { cleanup, render, screen, within } from '@testing-library/react';

import { log } from '@/logger';
import type { ListingEntity } from '@/types';
import { ListingDetailsCard } from './index';

const logger = log.getLogger(`${ListingDetailsCard.name}_tests`);

const baseListing: ListingEntity = {
  id: 'f6e6f5b0-1a2b-4c3d-8e9f-0123456789ab',
  created_at: '2024-01-01T00:00:00.000Z',
  updated_at: '2024-01-01T00:00:00.000Z',
  airroi_id: 'airroi-123',
  amenities: ['Wifi', 'Pool', 'Wifi'],
  baths: 2,
  beds: 3,
  bedrooms: 2,
  cover_photo_url: 'https://example.com/photo.jpg',
  description: 'A lovely little property.',
  latitude: 12.3456,
  location: '123 Main St',
  longitude: -65.4321,
  market_id: 'market-1',
  name: 'Cozy Cabin',
  photo_urls: ['https://example.com/photo.jpg'],
  property_type: 'Cabin',
  source_url: 'https://example.com/listing',
  listing_financial_reports: [],
};

describe('ListingDetailsCard', () => {
  afterEach(() => {
    cleanup();
  });

  it('should render correctly', () => {
    const { container } = render(<ListingDetailsCard listing={baseListing} />);

    const card = container.querySelector(
      '.listing-overview-data__details .listing-overview-data__data-item',
    ) as HTMLElement;
    expect(card).toBeVisible();

    expect(screen.getByText('Property Type')).toBeVisible();
    expect(screen.getByText(baseListing.property_type)).toBeVisible();

    expect(screen.getByText('Beds & Baths')).toBeVisible();
    expect(screen.getByText(`${baseListing.bedrooms} Bedrooms`)).toBeVisible();
    expect(screen.getByText(`${baseListing.beds} Beds`)).toBeVisible();
    expect(screen.getByText(`${baseListing.baths} Baths`)).toBeVisible();

    expect(screen.getByText('Amenities')).toBeVisible();
    expect(container.querySelector('.amenities-list')).toBeVisible();
  });

  it('should de-duplicate amenities', () => {
    const { container } = render(<ListingDetailsCard listing={baseListing} />);

    const amenitiesList = container.querySelector('.amenities-list') as HTMLElement;

    expect(amenitiesList).toBeVisible();
    const amenityEls = within(amenitiesList).getAllByText(/Wifi|Pool/);
    expect(amenityEls).toHaveLength(2);
    expect(amenityEls.map((el) => el.textContent)).toEqual(['Wifi', 'Pool']);
  });

  it('should default beds and baths to 0 when not provided', () => {
    render(
      <ListingDetailsCard
        listing={{ ...baseListing, beds: undefined, baths: undefined }}
      />,
    );

    expect(screen.getByText('0 Beds')).toBeVisible();
    expect(screen.getByText('0 Baths')).toBeVisible();
  });

  it('should render no amenities when the list is empty', () => {
    const { container } = render(
      <ListingDetailsCard listing={{ ...baseListing, amenities: [] }} />,
    );

    const amenitiesList = container.querySelector('.amenities-list') as HTMLElement;

    expect(amenitiesList).toBeVisible();
    expect(amenitiesList).toHaveTextContent('No amenities listed 😕');
  });
});
