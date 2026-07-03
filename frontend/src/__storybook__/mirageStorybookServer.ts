import { createServer, type Request as MirageRequest } from 'miragejs';

const BASE_DATA_SERVER_URL = 'http://localhost:3030/mock-data/api';

const endpointTypes = ['markets'];

const DEFAULT_ARGS = {
  enableLogging: false,
};

export const createMirageStorybookServer = ({
  enableLogging = DEFAULT_ARGS.enableLogging,
}: { enableLogging: boolean } = DEFAULT_ARGS) =>
  createServer({
    // environment: 'storybook',
    logging: enableLogging,

    routes() {
      // this.urlPrefix = 'http://localhost:6006/api';
      // this.namespace = 'api';

      for (const endpointType of endpointTypes) {
        const routePath = `${endpointType}`;
        console.log({
          routePath,
        });

        this.get(`/api/${routePath}/:entityId`, async (schema, request) => {
          return getRequestFactory({ endpointPath: routePath, request });
        });

        this.get(`/api/${routePath}`, async (schema, request) => {
          console.log({
            requestUrl: request.url,
          });
          return getRequestFactory({ endpointPath: routePath, request });
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
      debugger;
      console.error(
        `[MOCK - /api/${endpointPath}] Encountered unexpected error: `,
        error,
      );
      return error;
    });
}
