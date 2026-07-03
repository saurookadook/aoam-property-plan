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
import { MarketsList } from './index';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 10, // 10 seconds
    },
  },
});

function MarketsListWithQueryProvider() {
  return (
    <QueryClientProvider client={queryClient}>
      <MarketsList />
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

    let marketsListWrapper: HTMLDivElement;

    await waitFor(() => {
      marketsListWrapper = container.querySelector(
        '.markets-list__wrapper',
      ) as HTMLDivElement;
      expect(marketsListWrapper).toBeVisible();
    });

    const marketsListItems = marketsListWrapper!.children;
    expect(marketsListItems).toHaveLength(3);
    Array.from(marketsListItems).forEach((listItem) => {
      expect(listItem).toBeVisible();
    });
  });
});
