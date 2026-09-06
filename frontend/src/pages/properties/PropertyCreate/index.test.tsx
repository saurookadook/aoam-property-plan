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

function PropertyCreateWithQueryProvider() {
  return (
    <QueryClientProvider client={queryClient}>
      <AppThemeProvider>
        <WithMemoryRouter initialEntries={[`/properties/new`]} />
      </AppThemeProvider>
    </QueryClientProvider>
  );
}

describe('PropertyCreate', () => {
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

  async function renderPropertyCreate() {
    const { container, user } = renderWithContext(
      <PropertyCreateWithQueryProvider />,
      AppStateProvider,
    );

    await waitFor(() => {
      expect(container.querySelector('.property-create')).toBeVisible();
    });

    return { container, user };
  }

  it('the manual submit button is disabled until every required field is filled', async () => {
    const { user } = await renderPropertyCreate();

    await user.click(
      screen.getByRole('button', { name: "This isn't a Finca Raiz listing" }),
    );

    const manualSubmit = screen.getByRole('button', {
      name: 'Add property (manual entry)',
    });
    expect(manualSubmit).toBeDisabled();
  });

  it('creates a property from a URL and navigates to its deep-dive page', async () => {
    const { container, user } = await renderPropertyCreate();

    await user.type(
      screen.getByPlaceholderText('https://www.fincaraiz.com.co/inmueble/...'),
      'https://example.com/x',
    );
    await user.click(screen.getByRole('button', { name: 'Add property' }));

    await waitFor(() => {
      expect(
        container.querySelector('#property-overview'),
      ).toBeVisible();
    });

    expect(container.textContent).toContain('Finca Cocora');
  });
});
