import type { PropsWithChildren } from 'react';
import { QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';

import { queryClient } from '@/app/browserRouter';

export function QueryProviderWrapper({ children }: PropsWithChildren) {
  const rqDevToolsEnabled = window.localStorage.getItem('rqDevToolsEnabled');

  return (
    <QueryClientProvider client={queryClient}>
      {children}

      {rqDevToolsEnabled != null && rqDevToolsEnabled === 'true' && (
        <ReactQueryDevtools
          buttonPosition="bottom-right"
          // initialIsOpen={false}
        />
      )}
    </QueryClientProvider>
  );
}
