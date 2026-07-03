import type { EndpointConfig } from '@/types';

export const baseEndpointConfig = {
  errorMessage: 'Internal server error',
  logName: 'MOCK test server',
} as const;

export const endpointConfigs: EndpointConfig[] = [
  {
    ...baseEndpointConfig,
    type: 'list',
    emptyResult: {
      data: [],
    },
    errorMessage: 'Error fetching markets',
    entityType: 'markets',
    // filenamePrefix: 'all',
  },
];
