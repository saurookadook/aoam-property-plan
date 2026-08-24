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
    errorMessage: 'Error fetching listing overview',
    entityType: 'listings',
    filenamePrefix: 'highest-earners',
    fullPath: 'home/listings/highest-earners',
  },
  {
    ...baseEndpointConfig,
    type: 'list',
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
  {
    ...baseEndpointConfig,
    type: 'list',
    emptyResult: {
      data: null,
    },
    errorMessage: 'Error fetching exchange rate',
    entityType: 'exchange-rate',
  },
  {
    ...baseEndpointConfig,
    type: 'list',
    emptyResult: {
      data: [],
    },
    errorMessage: 'Error fetching properties',
    entityType: 'properties',
  },
  {
    ...baseEndpointConfig,
    type: 'list',
    emptyResult: {
      data: null,
    },
    errorMessage: 'Error creating property',
    entityType: 'properties',
    filenamePrefix: 'created',
    method: 'POST',
  },
  {
    ...baseEndpointConfig,
    type: 'overview',
    emptyResult: {
      data: null,
    },
    errorMessage: 'Error fetching property',
    entityIdPathParam: 'propertyId',
    entityType: 'properties',
  },
  {
    ...baseEndpointConfig,
    type: 'sub-resource',
    emptyResult: {
      data: null,
    },
    errorMessage: 'Error fetching property report',
    entityIdPathParam: 'propertyId',
    entityType: 'properties',
    subPath: ['report'],
  },
  {
    ...baseEndpointConfig,
    type: 'sub-resource',
    emptyResult: {
      data: null,
    },
    errorMessage: 'Error analyzing property',
    entityIdPathParam: 'propertyId',
    entityType: 'properties',
    method: 'POST',
    subPath: ['analyze'],
  },
  {
    ...baseEndpointConfig,
    type: 'sub-resource',
    emptyResult: {
      data: [],
    },
    errorMessage: 'Error fetching property comps',
    entityIdPathParam: 'propertyId',
    entityType: 'properties',
    subPath: ['comps'],
  },
  {
    ...baseEndpointConfig,
    type: 'sub-resource',
    emptyResult: {
      data: [],
    },
    errorMessage: 'Error fetching cached property comps',
    entityIdPathParam: 'propertyId',
    entityType: 'properties',
    subPath: ['comps', 'cached'],
  },
];
