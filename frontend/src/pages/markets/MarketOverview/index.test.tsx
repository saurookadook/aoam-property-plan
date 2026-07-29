import {
  afterAll, // force formatting
  afterEach,
  beforeAll,
  beforeEach,
  describe,
  expect,
  it,
  test,
  vi,
} from 'vitest';
import { cleanup, screen, waitFor, within } from '@testing-library/react';
import renderWithContext from '#saurookkadookk/react-utils-render-with-context';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

import { createMirageTestServer } from '@/__mocks__/mirageTestServer';
import { AppStateProvider } from '@/store';
import { WithMemoryRouter } from '@/utils/testing';

const queryClient = new QueryClient();

function MarketOverviewWithRouterAndQueryProvider({ marketId }: { marketId: string }) {
  return (
    <QueryClientProvider client={queryClient}>
      <WithMemoryRouter initialEntries={[`/markets/${marketId}`]} />
    </QueryClientProvider>
  );
}

describe('MarketOverview', () => {
  let mirageServer: ReturnType<typeof createMirageTestServer>;

  beforeEach(() => {
    mirageServer = createMirageTestServer();
    vi.clearAllMocks();
  });

  afterEach(() => {
    mirageServer.shutdown();
    cleanup();
    vi.clearAllMocks();
  });

  it('should render correctly', async () => {
    const { container } = renderWithContext(
      <MarketOverviewWithRouterAndQueryProvider marketId="7e1960b2-a442-410d-96ba-d302e3ad684b" />,
      AppStateProvider,
    );

    let marketOverviewDataEl: HTMLDivElement;

    await waitFor(() => {
      marketOverviewDataEl = container.querySelector(
        '.market-overview__wrapper .market-overview-data',
      ) as HTMLDivElement;
      expect(marketOverviewDataEl).toBeVisible();
    });

    const marketOverviewDataCard = marketOverviewDataEl!.querySelector(
      '.market-overview-data__data-item',
    ) as HTMLElement;

    expect(marketOverviewDataCard).toBeVisible();
    const localityHeading = within(marketOverviewDataCard).getByRole('heading', {
      level: 2,
    });
    expect(localityHeading).toBeVisible();
    expect(localityHeading).not.toBeEmptyDOMElement();

    for (const detail of ['region', 'country']) {
      const detailSpan = marketOverviewDataCard.querySelector(
        `.market-overview-data__data-item__${detail}`,
      ) as HTMLElement;
      expect(detailSpan).toBeVisible();
      expect(detailSpan).not.toBeEmptyDOMElement();
    }

    const listingTiles = marketOverviewDataEl!.querySelectorAll(
      '.market-overview-data .listing-paper-tile',
    );
    expect(listingTiles.length).toBeGreaterThan(0);
    listingTiles.forEach((tile) => {
      expect(tile).toBeVisible();

      const label = tile.querySelector('.listing-paper-tile__label');
      expect(label).toBeVisible();
      expect(label).not.toBeEmptyDOMElement();

      const img = tile.querySelector(
        'img.listing-paper-tile__image',
      ) as HTMLImageElement;
      expect(img).toBeVisible();
      expect(img.src).not.toStrictEqual('');
    });
  });
});
