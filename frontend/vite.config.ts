/// <reference types="vitest/config" />
import path from 'path';
import { defineConfig, type LogLevel, type UserConfig } from 'vite';
import type { InlineConfig } from 'vitest/node';
import react from '@vitejs/plugin-react';

const __dirname = path.resolve();

const ViteLogLevels = {
  INFO: 'info',
  WARN: 'warn',
  ERROR: 'error',
  SILENT: 'silent',
} as const;

const { LOG_LEVEL, SERVER_PORT } = process.env;

const configLogLevel =
  LOG_LEVEL != null && LOG_LEVEL in ViteLogLevels // force formatting
    ? (LOG_LEVEL as LogLevel)
    : 'info';

type ViteConfig = UserConfig & { test: InlineConfig; logLevel?: LogLevel };

const config: ViteConfig = {
  logLevel: configLogLevel,
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src/'),
    },
  },
  test: {
    alias: {
      /* Fixes for module resolutions */
      '#saurookkadookk/react-utils-render-with-context': path.resolve(
        __dirname,
        '../node_modules/@saurookkadookk/react-utils-render-with-context/dist/esm',
      ),
    },
    environment: 'jsdom',
    include: [
      '**/*.{test,spec}.{js,jsx,ts,tsx}', // force formatting
      '**/__tests__/**/*.{ts,tsx}',
    ],
    reporters: ['verbose'],
    sequence: {
      hooks: 'list',
    },
    setupFiles: ['./vitest.setup.ts'],
  },
};

// https://vite.dev/config/
export default defineConfig(config);
