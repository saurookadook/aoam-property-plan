import type { EndpointConfig } from '@/types';

export const baseEndpointConfig = {
  errorMessage: 'Internal server error',
  logName: 'MOCK test server',
} as const;

export const endpointConfigs: EndpointConfig[] = [
  {
    ...baseEndpointConfig,
    type: 'home',
    emptyResult: {
      data: [],
    },
    errorMessage: 'Error fetching listing overview',
    entityType: 'listings',
    filenamePrefix: 'highest-earners',
    fullPath: 'home/listings/highest-earners',
  },
  {
    ...baseEndpointConfig,
    type: 'home',
    emptyResult: {
      data: [],
    },
    errorMessage: 'Error fetching listing overview',
    entityType: 'listings',
    filenamePrefix: 'newest',
    fullPath: 'home/listings/newest',
  },
  {
    ...baseEndpointConfig,
    type: 'overview',
    emptyResult: {
      data: null,
    },
    errorMessage: 'Error fetching listing overview',
    entityIdPathParam: 'listingId',
    entityType: 'listings',
    // filenamePrefix: 'all',
  },
  {
    ...baseEndpointConfig,
    type: 'overview',
    emptyResult: {
      data: {
        market: null,
        listings: [],
      },
    },
    errorMessage: 'Error fetching market overview',
    entityIdPathParam: 'marketId',
    entityType: 'markets',
    // filenamePrefix: 'all',
  },
  {
    ...baseEndpointConfig,
    type: 'list',
    emptyResult: {
      data: [],
    },
    errorMessage: 'Error fetching markets',
    entityType: 'markets',
  },
];
