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

function MarketsListWithQueryProvider() {
  return (
    <QueryClientProvider client={queryClient}>
      <WithMemoryRouter initialEntries={[`/markets`]} />
    </QueryClientProvider>
  );
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

  it('should render correctly', async () => {
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

    const marketsListItems = marketsListDataEl!.querySelectorAll(
      '.markets-list-data__data-item',
    );
    expect(marketsListItems).toHaveLength(3);
    Array.from(marketsListItems).forEach((listItem) => {
      expect(listItem).toBeVisible();
    });
  });
});
