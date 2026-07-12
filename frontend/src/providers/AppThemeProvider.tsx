import type { PropsWithChildren } from 'react';
import { CssBaseline, ThemeProvider } from '@mui/material';

import { muiTheme } from '@/constants';

export const colorSchemeKey = 'aoam-color-scheme';

export const colorSchemeManager = function colorSchemeManager({}) {
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

export function AppThemeProvider({ children }: PropsWithChildren) {
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
