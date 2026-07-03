import { useEffect, useRef } from 'react';
import { MemoryRouter } from 'react-router';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import type { Decorator } from '@storybook/react-vite';

import { createMirageStorybookServer } from '../src/__storybook__/mirageStorybookServer';

import '../src/index.css';
import '../src/app/App.scss';

export const MemoryRouterDecorator: Decorator = (Story) => {
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

export const MirageServerDecorator: Decorator = (Story) => {
  const serverRef = useRef<ReturnType<typeof createMirageStorybookServer> | null>(null);

  useEffect(() => {
    serverRef.current = createMirageStorybookServer();

    return () => {
      serverRef.current?.shutdown();
    };
  });

  return <Story />;
};

export const globalStoryDecorators: Decorator[] = [
  MemoryRouterDecorator,
  QueryClientDecorator,
  MirageServerDecorator, // force formatting
];
