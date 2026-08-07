import http from 'http';
import path from 'path';
import type { Request as ExpressRequest } from 'express';
import type { Request as MirageRequest } from 'miragejs';

import type {
  EndpointConfig,
  KeyedObject,
  MockResponse,
  MockResponseCache,
} from '@/types';
import { buildPathToGzippedData, readGzippedJson } from './filesystem';
import {
  create200Response,
  create400Response,
  create500Response,
} from './responseFactories';

const baseDir = path.resolve();

export async function dataRequestHandler(
  request: ExpressRequest | MirageRequest,
  mockResponseCache: MockResponseCache,
  config: EndpointConfig,
) {
  logProxy(`[${config.logName} - /api/${config.type}] request: `, {
    params: request.params,
    url: request.url,
  });

  try {
    const { params } = request;

    const entityType = (params?.entityType ??
      config?.fullPath ??
      config.entityType) as string;
    const filenamePrefix = (params?.entityId ??
      config?.filenamePrefix ??
      'list') as string;
    const filePathForRequest = buildPathToGzippedData({
      entityType,
      filenamePrefix,
    });
    const compositeKey = buildCompositeKey(config, filenamePrefix);
    logProxy(`[${config.logName} - /api/${config.type}] before reading file: `, {
      compositeKey,
      entityType,
      filenamePrefix,
      filePathForRequest,
      params,
    });

    return boundReadGzippedJson(filePathForRequest)
      .then((jsonData) => {
        logProxy(`[${config.logName} - /api/${config.type}] after reading file: `, {
          compositeKey,
          entityType,
          filenamePrefix,
          filePathForRequest,
          params,
          jsonData,
        });

        if (!jsonData?.data?.length && config.emptyResultMessage != null) {
          mockResponseCache[compositeKey] = create400Response(
            config.emptyResultMessage,
          );
        } else {
          // NOTE: this is a little redundant but ¯\_(ツ)_/¯
          mockResponseCache[compositeKey] = create200Response(jsonData.data);
        }

        return mockResponseCache[compositeKey];
      })
      .catch((error) => {
        console.error(
          `[${config.logName} - /api/${config.type}] Encountered unexpected error: `,
          error,
        );
        mockResponseCache[compositeKey] = create500Response();
        return mockResponseCache[compositeKey];
      });
  } catch (exception: unknown) {
    const error = exception instanceof Error ? exception : new Error(String(exception));
    console.error(
      `[${config.logName} - /api/${config.type}] Encountered unexpected error: `,
      error,
    );
    return create500Response();
  }
}

export function safeGetBodyJson<T>(
  request: ExpressRequest | MirageRequest,
  fallback: T,
): T {
  /**
   * @note Comparing `http.IncomingMessage` because `ExpressRequest` extends it
   * and apparently `miragejs` doesn't export its `Request` class as an executable.
   */
  const requestBody =
    request instanceof http.IncomingMessage ? request.body : request.requestBody;

  if (requestBody == null) {
    return fallback;
  }

  if (typeof requestBody === 'string') {
    try {
      return JSON.parse(requestBody) as T;
    } catch (error: unknown) {
      return fallback;
    }
  }

  return requestBody;
}

export async function pollForMockResponse<T = MockResponse>(
  mockResponseCache: MockResponseCache,
  cacheKey: string,
): Promise<T> {
  return new Promise(function (resolve, reject) {
    const maxRetries = 50;
    let retryCount = 0;

    const pollForResult = setInterval(function () {
      logProxy(
        `Retry count: ${retryCount} for cacheKey: ${cacheKey}`,
        mockResponseCache,
      );
      if (mockResponseCache[cacheKey] != null) {
        clearInterval(pollForResult);
        resolve(mockResponseCache[cacheKey] as T);
      } else if (retryCount >= maxRetries) {
        clearInterval(pollForResult);
        reject(new Error(`Max retries reached for cacheKey: ${cacheKey}`));
      }
      retryCount++;
    }, 100);
  });
}

function buildCompositeKey(config: EndpointConfig, filenamePrefix: string) {
  return [
    config.type, // force formatting
    config.entityType,
    filenamePrefix,
  ].join('_');
}

async function boundReadGzippedJson(filePath: string): Promise<KeyedObject> {
  [
    '\n',
    ''.padEnd(100, '!'),
    `[boundReadGzippedJson] Attempting to read gzipped JSON from:`,
    `    baseDir: ${baseDir}`,
    `    filePath: ${filePath}`,
    ''.padEnd(100, '!'),
    '\n',
  ].forEach((line) => logProxy(line));

  return readGzippedJson(filePath);
}

function logProxy(...args: any[]) {
  // if (process.env.ENABLE_MOCK_SERVER_LOGGING !== 'true') return;

  console.log(...args);
}
