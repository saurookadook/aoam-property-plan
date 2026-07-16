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

function ListingOverviewWithRouterAndQueryProvider({
  listingId,
}: {
  listingId: string;
}) {
  return (
    <QueryClientProvider client={queryClient}>
      <WithMemoryRouter initialEntries={[`/listings/${listingId}`]} />
    </QueryClientProvider>
  );
}

describe('ListingOverview', () => {
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
      <ListingOverviewWithRouterAndQueryProvider listingId="0fa060df-d145-4fcf-91ad-d0d2501562ad" />,
      AppStateProvider,
    );

    let listingOverviewDataEl: HTMLDivElement;

    await waitFor(() => {
      listingOverviewDataEl = container.querySelector(
        '.listing-overview__wrapper .listing-overview-data',
      ) as HTMLDivElement;
      expect(listingOverviewDataEl).toBeVisible();
    });

    const listingOverviewDataCard = listingOverviewDataEl!.querySelector(
      '.listing-overview-data__data-item',
    ) as HTMLElement;

    expect(listingOverviewDataCard).toBeVisible();
    const localityHeading = within(listingOverviewDataCard).getByRole('heading', {
      level: 2,
    });
    expect(localityHeading).toBeVisible();
    expect(localityHeading).not.toBeEmptyDOMElement();

    const descriptionSpan = listingOverviewDataCard.querySelector(
        `.listing-overview-data__data-item__description`,
      ) as HTMLElement;
      expect(descriptionSpan).toBeVisible();
      expect(descriptionSpan).not.toBeEmptyDOMElement();
  });
});
