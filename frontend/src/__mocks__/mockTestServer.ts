import { createServer } from 'miragejs';

import type { MockResponseCache } from '@/types';
import { endpointConfigs } from '@/mock-data-server/constants';
import { dataRequestHandler } from '@/mock-data-server/utils';

const mockResponseCache: MockResponseCache = {};

export const mirageStorybookServer = () =>
  createServer({
    routes() {
      this.namespace = 'api';
      this.passthrough();

      for (const config of endpointConfigs) {
        const routePath = [
          config.entityType,
          config.type !== 'overview' ? ':entityId' : '',
        ].join('/');

        this.get(`/${routePath}`, (schema, request) => {
          return dataRequestHandler(request, mockResponseCache, config);
        });
      }
    },
  });
