import { StrictMode, type PropsWithChildren } from 'react';
import { createRoot } from 'react-dom/client';
import L from 'leaflet';
import markerIconUrl from 'leaflet/dist/images/marker-icon.png';
import markerIconRetinaUrl from 'leaflet/dist/images/marker-icon-2x.png';
import markerShadowUrl from 'leaflet/dist/images/marker-shadow.png';

import App from '@/app/App';
import { log } from '@/logger';
import { AppThemeProvider, QueryProviderWrapper } from '@/providers';
import { AppStateProvider } from '@/store';

import 'leaflet/dist/leaflet.css';
import '@/index.scss';

L.Icon.Default.imagePath = '';
L.Icon.Default.mergeOptions({
  iconUrl: markerIconUrl,
  iconRetinaUrl: markerIconRetinaUrl,
  shadowUrl: markerShadowUrl,
});

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
