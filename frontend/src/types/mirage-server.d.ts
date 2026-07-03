import { KeyedObject } from './main';

export type EmptyResult = KeyedObject;

export type EndpointConfig = {
  type: string;
  emptyResult: EmptyResult;
  emptyResultMessage?: string;
  entityId?: string;
  entityType?: string;
  errorMessage: string;
  filenamePrefix?: string;
  fullPath?: string;
  logName: string;
  loadSuccessResponseFactory?: () => KeyedObject;
  // requestBodyFallback:
  successStatusMessage?: string;
};

export type MockSuccessResponse<T = any> = MockResponse<T>;
export type MockErrorResponse = { detail: string };

export type MockResponse<T = any> = MockSuccessResponse<T> | MockErrorResponse;

export type MockResponseCache = KeyedObject<MockResponse | MockErrorResponse>;
