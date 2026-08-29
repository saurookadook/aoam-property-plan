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
import { cleanup, fireEvent, screen, waitFor, within } from '@testing-library/react';
import renderWithContext from '#saurookkadookk/react-utils-render-with-context';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

import { createMirageTestServer } from '@/__mocks__/mirageTestServer';
import { AppThemeProvider } from '@/providers';
import { AppStateProvider } from '@/store';
import { WithMemoryRouter } from '@/utils/testing';

const queryClient = new QueryClient();

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
  });

  async function renderMarketsList() {
    const { container } = renderWithContext(
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

    return { container, marketsListDataEl: marketsListDataEl! };
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
    const { marketsListDataEl } = await renderMarketsList();

    fireEvent.click(screen.getByRole('button', { name: 'ADR' }));

    await waitFor(() => {
      const marketCards = Array.from(marketsListDataEl.querySelectorAll('.market-card'));
      expect(marketCards.map(localityOf)).toEqual([
        'Calima',
        'Cartagena',
        'Pance',
        'Salento',
        'Medellín',
        'Cali',
        'Bogota Capital District - Municipality',
        'Santa Marta',
      ]);
    });
  });

  it('renders the empty state for a market with no financial report', async () => {
    const { marketsListDataEl } = await renderMarketsList();

    const santaMartaCard = Array.from(
      marketsListDataEl.querySelectorAll('.market-card'),
    ).find((card) => localityOf(card) === 'Santa Marta');

    expect(santaMartaCard).toBeDefined();
    expect(
      within(santaMartaCard as HTMLElement).getByText(
        'No financial report yet - this market has not been summarised.',
      ),
    ).toBeVisible();
  });

  it('flips displayed money when the currency toggle is used', async () => {
    const { marketsListDataEl } = await renderMarketsList();

    const calimaCard = Array.from(
      marketsListDataEl.querySelectorAll('.market-card'),
    ).find((card) => localityOf(card) === 'Calima') as HTMLElement;

    expect(calimaCard.textContent).toMatch(/857\.200/);

    fireEvent.click(screen.getByRole('button', { name: /Display amounts in USD/i }));

    await waitFor(() => {
      expect(calimaCard.textContent).toMatch(/\$214/);
    });
  });
});
