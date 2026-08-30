import {
  afterEach, // force formatting
  beforeEach,
  describe,
  expect,
  it,
  vi,
} from 'vitest';
import { cleanup, screen, waitFor, within } from '@testing-library/react';
import renderWithContext from '#saurookkadookk/react-utils-render-with-context';
import { QueryClientProvider } from '@tanstack/react-query';

import { queryClient } from '@/app/browserRouter';
import { createMirageTestServer } from '@/__mocks__/mirageTestServer';
import { AppThemeProvider } from '@/providers';
import { AppStateProvider } from '@/store';
import { WithMemoryRouter } from '@/utils/testing';

/**
 * The app's own singleton, not a fresh `QueryClient` - `marketsListLoader`
 * closes over this same instance (see `browserRouter.tsx`), and a fresh local
 * client here would read an empty cache the loader never populated, forcing
 * `useSuspenseQuery` to refetch a second time. See Problem 7 in the plan.
 */
function MarketsListWithQueryProvider() {
  return (
    <QueryClientProvider client={queryClient}>
      <AppThemeProvider>
        <WithMemoryRouter initialEntries={[`/markets`]} />
      </AppThemeProvider>
    </QueryClientProvider>
  );
}

function localityOf(cardEl: Element): string {
  return cardEl.querySelector('h3')?.textContent ?? '';
}

describe('MarketsList', () => {
  let mirageServer: ReturnType<typeof createMirageTestServer>;

  beforeEach(() => {
    mirageServer = createMirageTestServer();
    vi.clearAllMocks();
  });

  afterEach(() => {
    mirageServer.shutdown();
    cleanup();
    vi.clearAllMocks();
    // The app's own singleton, reused deliberately (see the note above) - clear
    // its cache so one test's fetch can't feed the next a stale result.
    queryClient.clear();
  });

  async function renderMarketsList() {
    const { container, user } = renderWithContext(
      <MarketsListWithQueryProvider />,
      AppStateProvider,
    );

    let marketsListDataEl: HTMLDivElement;

    await waitFor(() => {
      marketsListDataEl = container.querySelector(
        '.markets-list__wrapper .markets-list-data',
      ) as HTMLDivElement;
      expect(marketsListDataEl).toBeVisible();
    });

    return {
      container, // force formatting
      marketsListDataEl: marketsListDataEl!,
      user,
    };
  }

  it('renders one card per market', async () => {
    const { marketsListDataEl } = await renderMarketsList();

    const marketCards = marketsListDataEl.querySelectorAll('.market-card');
    expect(marketCards.length).toBe(8);
    Array.from(marketCards).forEach((card) => {
      expect(card).toBeVisible();
    });
  });

  it('defaults to fit score, descending', async () => {
    const { marketsListDataEl } = await renderMarketsList();

    const marketCards = Array.from(marketsListDataEl.querySelectorAll('.market-card'));
    expect(marketCards.map(localityOf)).toEqual([
      'Cartagena',
      'Pance',
      'Calima',
      'Salento',
      'Medellín',
      'Cali',
      'Bogota Capital District - Municipality',
      'Santa Marta',
    ]);
  });

  it('resorts by ADR when the ADR control is selected', async () => {
    const { marketsListDataEl, user } = await renderMarketsList();

    await user.click(screen.getByRole('button', { name: 'ADR' }));

    await waitFor(() => {
      const marketCards = Array.from(
        marketsListDataEl.querySelectorAll('.market-card'),
      );

      expect(marketCards.map(localityOf)).toEqual([
        'Bogota Capital District - Municipality',
        'Calima',
        'Pance',
        'Salento',
        'Cali',
        'Cartagena',
        'Medellín',
        'Santa Marta',
      ]);
    });
  });

  it('renders the empty state for a market with no financial report', async () => {
    const { marketsListDataEl } = await renderMarketsList();

    const santaMartaCard = Array.from(
      marketsListDataEl.querySelectorAll('.market-card'),
    ).find((card) => localityOf(card) === 'Santa Marta');

    expect(santaMartaCard).toBeVisible();
    expect(
      within(santaMartaCard as HTMLElement).getByText(
        'No financial report yet - this market has not been summarised.',
      ),
    ).toBeVisible();
  });

  it('flips displayed money when the currency toggle is used', async () => {
    const { marketsListDataEl, user } = await renderMarketsList();

    const calimaCard = Array.from(
      marketsListDataEl.querySelectorAll('.market-card'),
    ).find((card) => localityOf(card) === 'Calima') as HTMLElement;

    expect(calimaCard.textContent).toMatch(/857\.200/);

    await user.click(screen.getByRole('button', { name: /Display amounts in USD/i }));

    await waitFor(() => {
      expect(calimaCard.textContent).toMatch(/\$214/);
    });
  });
});
