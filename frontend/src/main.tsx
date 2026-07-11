import { StrictMode, type PropsWithChildren } from 'react';
import { createRoot } from 'react-dom/client';
import { CssBaseline, ThemeProvider } from '@mui/material';
import { QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';

import '@/index.css';
import App from '@/app/App';
import { queryClient } from '@/app/browserRouter';
import { muiTheme } from '@/constants';
import { log } from '@/logger';
import { AppStateProvider } from '@/store';

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

const colorSchemeKey = 'aoam-color-scheme';

const colorSchemeManager = function colorSchemeManager({}) {
  return {
    get: (defaultValue: any): any => {
      return window.localStorage.getItem(colorSchemeKey) ?? defaultValue;
    },
    set: (value: any): void => {
      window.localStorage.setItem(colorSchemeKey, value);
    },
    subscribe: (handler: (value: any) => void): (() => void) => {
      // implement me :D
      return () => {
        // implement cleanup :D
      };
    },
  };
};

function AppThemeProvider({ children }: PropsWithChildren) {
  return (
    <ThemeProvider
      defaultMode="dark"
      storageManager={colorSchemeManager}
      theme={muiTheme}
    >
      <CssBaseline />

      {children}
    </ThemeProvider>
  );
}

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
