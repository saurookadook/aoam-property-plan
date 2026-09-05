import {
  afterEach, // force formatting
  beforeEach,
  describe,
  expect,
  it,
  vi,
} from 'vitest';
import { cleanup, waitFor } from '@testing-library/react';
import renderWithContext from '#saurookkadookk/react-utils-render-with-context';
import { QueryClientProvider } from '@tanstack/react-query';

import { queryClient } from '@/app/browserRouter';
import { createMirageTestServer } from '@/__mocks__/mirageTestServer';
import { AppThemeProvider } from '@/providers';
import { AppStateProvider } from '@/store';
import { WithMemoryRouter } from '@/utils/testing';

function PropertiesListWithQueryProvider() {
  return (
    <QueryClientProvider client={queryClient}>
      <AppThemeProvider>
        <WithMemoryRouter initialEntries={[`/properties`]} />
      </AppThemeProvider>
    </QueryClientProvider>
  );
}

describe('PropertiesList', () => {
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

  async function renderPropertiesList() {
    const { container, user } = renderWithContext(
      <PropertiesListWithQueryProvider />,
      AppStateProvider,
    );

    let propertiesListEl: HTMLDivElement;

    await waitFor(() => {
      propertiesListEl = container.querySelector('.properties-list') as HTMLDivElement;
      expect(propertiesListEl).toBeVisible();
    });

    return { container, propertiesListEl: propertiesListEl!, user };
  }

  it('renders one row per property', async () => {
    const { propertiesListEl } = await renderPropertiesList();

    await waitFor(() => {
      const rows = propertiesListEl.querySelectorAll('.property-row');
      expect(rows.length).toBe(5);
    });
  });

  it('links each row to its deep-dive page', async () => {
    const { propertiesListEl } = await renderPropertiesList();

    await waitFor(() => {
      const link = propertiesListEl.querySelector(
        'a[href="/properties/8f2d6b04-7e19-4a35-8c60-d3b5194ae872"]',
      );
      expect(link).toBeVisible();
      expect(link?.textContent).toBe('Casa Lago Calima');
    });
  });

  it('links to the create form', async () => {
    const { propertiesListEl } = await renderPropertiesList();

    const addLink = propertiesListEl.querySelector('a[href="/properties/new"]');
    expect(addLink).toBeVisible();
  });
});
