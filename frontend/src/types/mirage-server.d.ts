import { KeyedObject } from './main';

export type EmptyResult = KeyedObject;

export type EndpointConfig = {
  type: string;
  emptyResult: EmptyResult;
  entityId?: string;
  entityType?: string;
  filenamePrefix?: string;
  fullPath?: string;
  logName: string;
  loadSuccessResponseFactory?: () => KeyedObject;
  // requestBodyFallback:
  successStatusMessage?: string;
};

/** @deprecated Use `MockSuccessResponse` instead. */
export type MockResponse<T = any> = { data: T; success?: boolean };

export type MockSuccessResponse<T = any> = MockResponse<T>;

export type MockErrorResponse = { detail: string };

export type MockResponseCache = KeyedObject<MockResponse | MockErrorResponse>;
