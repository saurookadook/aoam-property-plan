import util from 'util';
import express from 'express';

import type { MockResponseCache } from '@/types';
import { endpointConfigs } from '../constants';
import { buildRoutePath, dataRequestHandler } from '../utils';

const router = express.Router();

const mockResponseCache: MockResponseCache = {};

for (const config of endpointConfigs) {
  const routePath = buildRoutePath(config);
  console.log({
    endpointConfig: config,
    routePath,
  });

  router.get(`/${routePath}`, async (req, res) => {
    console.log(
      `[${req.method} ${req.originalUrl}] In mock data server route handler: \n`,
      util.inspect(
        { reqBody: req.body, reqParams: req.params, reqQuery: req.query },
        { colors: true, depth: 1 },
      ),
    );
    const response = await dataRequestHandler(req, mockResponseCache, config);
    res.json(response);
  });
}

export default router;
