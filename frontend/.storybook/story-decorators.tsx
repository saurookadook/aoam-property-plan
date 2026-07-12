import { useEffect, useRef } from 'react';
import { MemoryRouter } from 'react-router';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import type { Decorator } from '@storybook/react-vite';

import { createMirageStorybookServer } from '../src/__storybook__/mirageStorybookServer';
import { AppThemeProvider } from '../src/providers';

import '../src/index.scss';
import '../src/app/App.scss';

export const MemoryRouterDecorator: Decorator = (Story, context) => {
  if (context.parameters.reactRouter != null) {
    return <Story />;
  }

  return (
    <MemoryRouter>
      <Story />
    </MemoryRouter>
  );
};

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 10, // 10 seconds
    },
  },
});

export const QueryClientDecorator: Decorator = (Story) => {
  return (
    <QueryClientProvider client={queryClient}>
      <Story />
    </QueryClientProvider>
  );
};

export const AppThemeProviderDecorator: Decorator = (Story) => {
  return (
    <AppThemeProvider>
      <Story />
    </AppThemeProvider>
  );
};

export const MirageServerDecorator: Decorator = (Story) => {
  const serverRef = useRef<ReturnType<typeof createMirageStorybookServer> | null>(null);

  if (serverRef.current == null) {
    serverRef.current = createMirageStorybookServer();
  }

  useEffect(() => {
    return () => {
      serverRef.current?.shutdown();
      serverRef.current = null;
    };
  }, []);

  return <Story />;
};

export const globalStoryDecorators: Decorator[] = [
  MemoryRouterDecorator,
  QueryClientDecorator,
  AppThemeProviderDecorator,
  MirageServerDecorator, // force formatting
];
