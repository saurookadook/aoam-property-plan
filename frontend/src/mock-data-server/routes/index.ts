import express from 'express';

import type { MockResponseCache } from '@/types';
import { endpointConfigs } from '../constants';
import { dataRequestHandler } from '../utils';

const router = express.Router();

const mockResponseCache: MockResponseCache = {};

for (const config of endpointConfigs) {
  const routePath = [
    config.entityType,
    config.type !== 'overview' ? ':entityId' : '',
  ].join('/');

  router.get(`/${routePath}`, (req, res) => {
    // TODO: revisit this :]
    return dataRequestHandler(req, mockResponseCache, config);
  });
}

export default router;
