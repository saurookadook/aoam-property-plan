import express from 'express';

import type { MockResponseCache } from '@/types';
import { endpointConfigs } from '../constants';
import { buildRoutePath, dataRequestHandler } from '../utils';

const router = express.Router();

const mockResponseCache: MockResponseCache = {};

for (const config of endpointConfigs) {
  const routePath = buildRoutePath(config);

  router.get(`/${routePath}`, async (req, res) => {
    const response = await dataRequestHandler(req, mockResponseCache, config);
    res.json(response);
  });
}

export default router;
