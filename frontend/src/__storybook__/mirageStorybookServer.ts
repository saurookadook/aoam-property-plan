import { createServer, type Request as MirageRequest } from 'miragejs';

import type { EndpointConfig } from '@/types';
import { endpointConfigs } from '@/constants';

const BASE_DATA_SERVER_URL = 'http://localhost:3030/mock-data/api';

const DEFAULT_ARGS = {
  enableLogging: false,
};

export const createMirageStorybookServer = ({
  enableLogging = DEFAULT_ARGS.enableLogging,
}: { enableLogging: boolean } = DEFAULT_ARGS) =>
  createServer({
    logging: enableLogging,

    routes() {
      this.urlPrefix = 'http://localhost:6006';
      this.namespace = 'api';

      for (const config of endpointConfigs) {
        const routePath = buildMirageStorybookRoutePath(config);
        console.log({
          routePath,
        });

        this.get(`/${routePath}`, async (schema, request) => {
          const endpointPathWithParams = Object.entries(request.params).reduce(
            (path, [paramKey, paramValue]) =>
              path.replace(`:${paramKey}`, String(paramValue)),
            routePath,
          );
          console.log({
            requestUrl: request.url,
            requestParams: request.params,
            routePath,
            endpointPath: endpointPathWithParams,
          });
          return getRequestFactory({ endpointPath: endpointPathWithParams, request });
        });
      }

      this.passthrough('http://localhost:3030/**');
      this.passthrough();
    },
  });

async function getRequestFactory({
  endpointPath,
  request,
}: {
  endpointPath: string;
  request: MirageRequest;
}) {
  console.log(`[MOCK - /api/${endpointPath}] request: `, request);

  return fetch(`${BASE_DATA_SERVER_URL}/${endpointPath}`, {
    headers: {
      ...request.requestHeaders,
      'Access-Control-Allow-Origin': '*',
      'Content-Type': 'application/json',
    },
    method: 'GET',
  })
    .then((response) => response.json())
    .then((jsonResponse) => jsonResponse)
    .catch((error) => {
      // eslint-disable-next-line no-debugger
      debugger;
      console.error(
        `[MOCK - /api/${endpointPath}] Encountered unexpected error: `,
        error,
      );
      return error;
    });
}

function buildMirageStorybookRoutePath(config: EndpointConfig): string {
  if (config.fullPath != null) {
    return config.fullPath;
  }

  const resolvedTypeComponent = (function () {
    switch (config.type) {
      case 'overview':
        return `:${config.entityIdPathParam ?? 'entityId'}`;
      case 'list':
      default:
        return '';
    }
  })();

  return [
    config.entityType, // force formatting
    resolvedTypeComponent,
  ]
    .filter((pathComponent) => !!pathComponent)
    .join('/');
}
