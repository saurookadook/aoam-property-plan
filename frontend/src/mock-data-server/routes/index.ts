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

  const routeHandler = async (
    req: express.Request,
    res: express.Response,
  ): Promise<void> => {
    console.log(
      `[${req.method} ${req.originalUrl}] In mock data server route handler: \n`,
      util.inspect(
        { reqBody: req.body, reqParams: req.params, reqQuery: req.query },
        { colors: true, depth: 1 },
      ),
    );
    const response = await handler(req, mockResponseCache, config);
    res.json(response);
  };

  if (config.method === 'POST') {
    router.post(`/${routePath}`, routeHandler);
  } else {
    router.get(`/${routePath}`, routeHandler);
  }
}

export default router;
