import { createServer } from 'miragejs';

import type { MockResponseCache } from '@/types';
import { endpointConfigs } from '@/mock-data-server/constants';
import {
  buildRoutePath,
  dataRequestHandler,
  mutationRequestHandler,
} from '@/mock-data-server/utils';

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

        /**
         * @note `this.post` as well as `this.get`. Registering only `GET` left
         * `POST /properties` and `POST /properties/{id}/analyze` unroutable, so
         * no page test could cover a mutation.
         */
        if (config.method === 'POST') {
          this.post(`/${routePath}`, (schema, request) => {
            return mutationRequestHandler(request, mockResponseCache, config);
          });
          continue;
        }

        this.get(`/${routePath}`, (schema, request) => {
          return dataRequestHandler(request, mockResponseCache, config);
        });
      }

      this.passthrough();
    },
  });
