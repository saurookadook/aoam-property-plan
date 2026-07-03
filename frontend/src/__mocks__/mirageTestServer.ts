import { createServer } from 'miragejs';

import type { MockResponseCache } from '@/types';
import { endpointConfigs } from '@/mock-data-server/constants';
import { buildRoutePath, dataRequestHandler } from '@/mock-data-server/utils';

const mockResponseCache: MockResponseCache = {};

const DEFAULT_ARGS = {
  enableLogging: false,
};

export const createMirageTestServer = ({
  enableLogging = DEFAULT_ARGS.enableLogging,
}: { enableLogging: boolean } = DEFAULT_ARGS) =>
  createServer({
    environment: 'test',
    logging: enableLogging,

    routes() {
      this.namespace = 'api';

      for (const config of endpointConfigs) {
        const routePath = buildRoutePath(config);

        this.get(`/${routePath}`, (schema, request) => {
          return dataRequestHandler(request, mockResponseCache, config);
        });
      }

      this.passthrough();
    },
  });
