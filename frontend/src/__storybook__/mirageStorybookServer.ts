import { createServer, type Request as MirageRequest } from 'miragejs';

const BASE_DATA_SERVER_URL = 'http://localhost:3030/mock-data/api';

const endpointTypes = ['markets'];

const getRequestFactory = async ({
  endpointPath,
  request,
}: {
  endpointPath: string;
  request: MirageRequest;
}) => {
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
};

export const mirageStorybookServer = () =>
  createServer({
    routes() {
      this.namespace = 'api';
      this.passthrough();

      for (const endpointType of endpointTypes) {
        const routePath = `${endpointType}`;

        this.get(`/${routePath}`, async (schema, request) => {
          return getRequestFactory({ endpointPath: routePath, request });
        });

        this.get(`/${routePath}/:entityId`, async (schema, request) => {
          return getRequestFactory({ endpointPath: routePath, request });
        });
      }
    },
  });
