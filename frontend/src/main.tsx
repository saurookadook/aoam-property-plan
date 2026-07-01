import { StrictMode, type PropsWithChildren } from 'react';
import { createRoot } from 'react-dom/client';
import { QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';

import '@/index.css';
import App from '@/app/App';
import { queryClient } from '@/app/browserRouter';
import { log } from '@/logger';
import { AppStateProvider } from '@/store';

function InitApp({ children }: PropsWithChildren) {
  const enableStrictMode = window.localStorage.getItem('aoamStrictMode');

  const ENV_LOG_LEVEL: string = import.meta.env.LOG_LEVEL || 'SILENT';
  log.setLevel(ENV_LOG_LEVEL.toLowerCase() as log.LogLevelDesc);

  return enableStrictMode != null && enableStrictMode ? (
    <StrictMode>{children}</StrictMode>
  ) : (
    children
  );
}

function QueryProviderWrapper({ children }: PropsWithChildren) {
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

const rootEl = document.getElementById('root');
if (!rootEl) throw new Error('Missing #root element');

createRoot(rootEl).render(
  <InitApp>
    <AppStateProvider>
      <QueryProviderWrapper>
        <App />
      </QueryProviderWrapper>
    </AppStateProvider>
  </InitApp>,
);
