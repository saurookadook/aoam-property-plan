import {
  createServer,
  type Request as MirageRequest,
  Response as MirageResponse,
} from 'miragejs';

import { endpointConfigs } from '@/constants';
import { buildRoutePath } from '@/mock-data-server/utils/routing';

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
        const routePath = buildRoutePath(config);
        // console.log({
        //   routePath,
        // });

        const method = config.method === 'POST' ? this.post : this.get;

        method.call(
          this,
          `/${routePath}`,
          async (schema: unknown, request: MirageRequest) => {
            const endpointPathWithParams = Object.entries(request.params).reduce(
              (path, [paramKey, paramValue]) =>
                path.replace(`:${paramKey}`, String(paramValue)),
              routePath,
            );
            // console.log({
            //   requestUrl: request.url,
            //   requestParams: request.params,
            //   routePath,
            //   endpointPath: endpointPathWithParams,
            // });
            return proxyToDataServer({
              endpointPath: endpointPathWithParams,
              method: config.method ?? 'GET',
              request,
            });
          },
        );
      }

      this.passthrough('http://localhost:3030/**');
      this.passthrough();
    },
  });

async function proxyToDataServer({
  endpointPath,
  method,
  request,
}: {
  endpointPath: string;
  method: 'GET' | 'POST';
  request: MirageRequest;
}) {
  console.log(`[MOCK - /api/${endpointPath}] request: `, request);

  const response = await fetch(`${BASE_DATA_SERVER_URL}/${endpointPath}`, {
    body: method === 'POST' ? (request.requestBody ?? '{}') : undefined,
    headers: {
      ...request.requestHeaders,
      'Access-Control-Allow-Origin': '*',
      'Content-Type': 'application/json',
    },
    method,
  })
    .then((response) => response.json())
    .then((jsonResponse) => jsonResponse)
    .catch((error) => {
      console.error(
        `[MOCK - /api/${endpointPath}] Encountered unexpected error: `,
        error,
      );
      return error;
    });

  return new MirageResponse(response.status ?? 200, {}, response);
}
