import {
  afterEach, // force formatting
  beforeEach,
  describe,
  expect,
  it,
  vi,
} from 'vitest';
import { cleanup, screen, waitFor } from '@testing-library/react';
import renderWithContext from '#saurookkadookk/react-utils-render-with-context';
import { QueryClientProvider } from '@tanstack/react-query';

import { queryClient } from '@/app/browserRouter';
import { createMirageTestServer } from '@/__mocks__/mirageTestServer';
import { AppThemeProvider } from '@/providers';
import { AppStateProvider } from '@/store';
import { WithMemoryRouter } from '@/utils/testing';

const CALIMA_ID = '8f2d6b04-7e19-4a35-8c60-d3b5194ae872';
const SALENTO_ID = '3a1c8f52-0d47-4e69-9b83-5c2a7e1d40f6';
const NEVER_ANALYSED_ID = '2e8a5f13-6d90-4c47-8b25-71c3e9d0a4f8';

function PropertyOverviewWithQueryProvider({ propertyId }: { propertyId: string }) {
  return (
    <QueryClientProvider client={queryClient}>
      <AppThemeProvider>
        <WithMemoryRouter initialEntries={[`/properties/${propertyId}`]} />
      </AppThemeProvider>
    </QueryClientProvider>
  );
}

describe('PropertyOverview', () => {
  let mirageServer: ReturnType<typeof createMirageTestServer>;

  beforeEach(() => {
    mirageServer = createMirageTestServer();
    vi.clearAllMocks();
  });

  afterEach(() => {
    mirageServer.shutdown();
    cleanup();
    vi.clearAllMocks();
    queryClient.clear();
  });

  async function renderPropertyOverview(propertyId: string) {
    const { container, user } = renderWithContext(
      <PropertyOverviewWithQueryProvider propertyId={propertyId} />,
      AppStateProvider,
    );

    let wrapperEl: HTMLDivElement;

    await waitFor(() => {
      wrapperEl = container.querySelector(
        '.property-overview__wrapper',
      ) as HTMLDivElement;
      expect(wrapperEl).toBeVisible();
    });

    return { container, user, wrapperEl: wrapperEl! };
  }

  it('shows a low-confidence banner and renders CoC/payback unrated for a thin-comps property', async () => {
    const { wrapperEl } = await renderPropertyOverview(CALIMA_ID);

    expect(
      screen.getByText(
        "Low confidence — AirROI's model only, 1 comparable listing.",
      ),
    ).toBeVisible();

    expect(wrapperEl.querySelectorAll('.metric-grid__tile--unrated').length).toBe(2);
    expect(
      wrapperEl.querySelectorAll(
        '.metric-grid__tile--good, .metric-grid__tile--fair, .metric-grid__tile--poor',
      ).length,
    ).toBe(0);
  });

  it('colours the CoC tile for a good-confidence property', async () => {
    const { wrapperEl } = await renderPropertyOverview(SALENTO_ID);

    expect(
      screen.getByText(/Good confidence — median of 12 comparable listings\./),
    ).toBeVisible();
    expect(wrapperEl.querySelectorAll('.metric-grid__tile--poor').length).toBe(1);
  });

  it('renders the 3-cell sensitivity sweep', async () => {
    const { wrapperEl } = await renderPropertyOverview(SALENTO_ID);

    const sensitivityTable = wrapperEl.querySelector('.sensitivity-table table');
    expect(sensitivityTable).toBeVisible();
    expect(sensitivityTable?.querySelectorAll('tbody tr')).toHaveLength(3);
  });

  it('renders the twelve-bar seasonality chart with an accessible title per bar', async () => {
    const { wrapperEl } = await renderPropertyOverview(CALIMA_ID);

    // Each bar's accessible name is a `<title>` nested inside its `<rect>`,
    // not a direct child of `<svg>` - `getByTitle`'s `svg > title` selector
    // does not reach it, so this queries the SVG title elements directly.
    const barTitles = Array.from(
      wrapperEl.querySelectorAll('.seasonality-chart__bar > title'),
    ).map((title) => title.textContent);

    expect(barTitles).toContain('July — 10.6% of annual revenue');
    expect(barTitles).toHaveLength(12);
  });

  it('renders the comps table with a link out to Airbnb', async () => {
    const { wrapperEl } = await renderPropertyOverview(CALIMA_ID);

    const link = wrapperEl.querySelector(
      'a[href="https://www.airbnb.com/rooms/41000001"]',
    );
    expect(link).toBeVisible();
    expect(link).toHaveAttribute('target', '_blank');
  });

  it('shows an Analyse panel, not the metric grid, for a never-analysed property', async () => {
    const { wrapperEl } = await renderPropertyOverview(NEVER_ANALYSED_ID);

    expect(
      screen.getByText('This property has not been analysed yet.'),
    ).toBeVisible();
    expect(wrapperEl.querySelector('.metric-grid')).toBeNull();
    expect(screen.getByRole('button', { name: 'Analyse' })).toBeInTheDocument();
  });

  it('re-analyses via the assumptions panel without a second navigation', async () => {
    const { user, wrapperEl } = await renderPropertyOverview(CALIMA_ID);

    const reAnalyseButton = screen.getByRole('button', { name: 'Re-analyse' });
    expect(reAnalyseButton).toBeEnabled();

    await user.click(reAnalyseButton);

    await waitFor(() => {
      expect(reAnalyseButton).toBeEnabled();
    });

    // Still on the same property page - the mutation updates in place.
    expect(wrapperEl.querySelector('.metric-grid')).toBeVisible();
  });
});
