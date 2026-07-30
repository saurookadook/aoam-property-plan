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
  LOG_LEVEL != null && (Object.values(ViteLogLevels) as string[]).includes(LOG_LEVEL) // force formatting
    ? (LOG_LEVEL as LogLevel)
    : 'info';

type ViteConfig = UserConfig & { test: InlineConfig; logLevel?: LogLevel };

const config: ViteConfig = {
  build: {
    rolldownOptions: {
      output: {
        /** @see {@link https://rolldown.rs/reference/OutputOptions.codeSplitting | codeSplitting} */
        codeSplitting: {
          groups: [
            {
              name: 'react-vendor',
              test: /node_modules[\\/]react/,
              priority: 20,
            },
            {
              name: 'vendor',
              test: /node_modules[\\/](?!react)/,
              priority: 10,
            },
          ],
        },
      },
    },
  },
  css: {
    postcss: path.resolve(__dirname, './postcss.config.js'),
  },
  logLevel: configLogLevel,
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src/'),
    },
  },
  server: {
    allowedHosts: ['aoam.dev'],
    host: true,
    watch: {
      usePolling: true,
    },
  },
  test: {
    alias: {
      /* Fixes for module resolutions */
      '#saurookkadookk/react-utils-render-with-context': path.resolve(
        __dirname,
        './node_modules/@saurookkadookk/react-utils-render-with-context/dist/esm',
      ),
    },
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json-summary', 'json'],
      reportOnFailure: true, // to get coverage reports even if tests fail
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
