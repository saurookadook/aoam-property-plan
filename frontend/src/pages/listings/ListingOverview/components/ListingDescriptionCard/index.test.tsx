import { afterEach, describe, expect, it } from 'vitest';
import { cleanup, render, screen } from '@testing-library/react';

import { log } from '@/logger';
import { ListingDescriptionCard } from './index';

const logger = log.getLogger(`${ListingDescriptionCard.name}_tests`);

describe('ListingDescriptionCard', () => {
  afterEach(() => {
    cleanup();
  });

  it('should render correctly', () => {
    const { container } = render(
      <ListingDescriptionCard description="A lovely little property." />,
    );

    const card = container.querySelector(
      '.listing-overview-data__data-item',
    ) as HTMLElement;
    expect(card).toBeVisible();

    const descriptionEl = container.querySelector(
      '.listing-overview-data__data-item__description',
    ) as HTMLElement;
    expect(descriptionEl).toBeVisible();
    expect(descriptionEl).toHaveTextContent('A lovely little property.');
  });

  it('should receive props correctly', () => {
    const { container } = render(
      <ListingDescriptionCard
        className="test-class"
        description="A lovely little property."
      />,
    );

    const card = container.querySelector(
      '.listing-overview-data__data-item',
    ) as HTMLElement;
    expect(card).toHaveClass('test-class');
    expect(card).toHaveClass('listing-overview-data__data-item');
  });

  it('should render a fallback message when description is undefined', () => {
    const { container } = render(<ListingDescriptionCard />);

    const descriptionEl = container.querySelector(
      '.listing-overview-data__data-item__description',
    ) as HTMLElement;
    expect(descriptionEl).toBeVisible();
    expect(descriptionEl).toHaveTextContent('No description 🤷‍♂️');
  });

  it('should render a fallback message when description is an empty string', () => {
    const { container } = render(<ListingDescriptionCard description="" />);

    const descriptionEl = container.querySelector(
      '.listing-overview-data__data-item__description',
    ) as HTMLElement;
    expect(descriptionEl).toBeVisible();
    expect(descriptionEl).toHaveTextContent('No description 🤷‍♂️');
  });

  it('should sanitize HTML content in the description', () => {
    const { container } = render(
      <ListingDescriptionCard description="<b>Bold</b><script>alert('xss')</script> text" />,
    );

    const descriptionEl = container.querySelector(
      '.listing-overview-data__data-item__description',
    ) as HTMLElement;
    expect(descriptionEl.querySelector('script')).toBeNull();
    expect(descriptionEl.querySelector('b')).not.toBeNull();
    expect(descriptionEl).toHaveTextContent('Bold text');
  });
});
