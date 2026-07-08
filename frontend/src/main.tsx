import { StrictMode, type PropsWithChildren } from 'react';
import { createRoot } from 'react-dom/client';
import { ThemeProvider } from '@mui/material/styles';
import { QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';

import '@/index.css';
import App from '@/app/App';
import { queryClient } from '@/app/browserRouter';
import { muiTheme } from '@/constants';
import { log } from '@/logger';
import { AppStateProvider } from '@/store';

function InitApp({ children }: PropsWithChildren) {
  const enableStrictMode = window.localStorage.getItem('aoamStrictMode') === 'true';

  const ENV_LOG_LEVEL: string = import.meta.env.VITE_LOG_LEVEL || 'SILENT';
  log.setLevel(ENV_LOG_LEVEL.toLowerCase() as log.LogLevelDesc);

  return enableStrictMode ? ( // force formatting
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

function AppThemeProvider({ children }: PropsWithChildren) {
  return <ThemeProvider theme={muiTheme}>{children}</ThemeProvider>;
}

const rootEl = document.getElementById('root');
if (!rootEl) throw new Error('Missing #root element');

createRoot(rootEl).render(
  <InitApp>
    <AppStateProvider>
      <AppThemeProvider>
        <QueryProviderWrapper>
          <App />
        </QueryProviderWrapper>
      </AppThemeProvider>
    </AppStateProvider>
  </InitApp>,
);
