import type { EndpointConfig } from '@/types';

export const baseEndpointConfig = {
  logName: 'MOCK test server',
} as const;

export const endpointConfigs: EndpointConfig[] = [
  {
    ...baseEndpointConfig,
    type: 'list',
    emptyResult: {
      data: [],
    },
    entityType: 'markets',
    // filenamePrefix: 'all',
  },
];
