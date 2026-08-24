import util from 'util';
import express from 'express';

import type { MockResponseCache } from '@/types';
import { endpointConfigs } from '../constants';
import { buildRoutePath, dataRequestHandler, mutationRequestHandler } from '../utils';

const router = express.Router();

const mockResponseCache: MockResponseCache = {};

for (const config of endpointConfigs) {
  const routePath = buildRoutePath(config);
  console.log({
    endpointConfig: config,
    routePath,
  });

  const handler =
    config.method === 'POST' ? mutationRequestHandler : dataRequestHandler;

  const routeHandler = createRouteHandler(config, handler);

  if (config.method === 'POST') {
    router.post(`/${routePath}`, routeHandler);
  } else {
    router.get(`/${routePath}`, routeHandler);
  }
}

function createRouteHandler(
  config: (typeof endpointConfigs)[number],
  handlerFn: typeof dataRequestHandler | typeof mutationRequestHandler,
): express.RequestHandler {
  return async (req: express.Request, res: express.Response) => {
    console.log(
      `[${req.method} ${req.originalUrl}] In mock data server route handler: \n`,
      util.inspect(
        { reqBody: req.body, reqParams: req.params, reqQuery: req.query },
        { colors: true, depth: 1 },
      ),
    );
    const response = await handlerFn(req, mockResponseCache, config);
    res.json(response);
  };
}

export default router;
