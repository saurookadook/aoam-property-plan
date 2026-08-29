import { KeyedObject } from './main';

export type EmptyResult = KeyedObject;

/**
 * `'sub-resource'` is the case `properties/{id}/comps` needs: an entity id
 * followed by extra path segments, which neither `'list'` nor `'overview'`
 * could express.
 */
export type EndpointType = 'list' | 'overview' | 'sub-resource';

export type EndpointMethod = 'GET' | 'POST';

export type EndpointConfig = {
  type: EndpointType;
  emptyResult: EmptyResult;
  emptyResultMessage?: string;
  entityId?: string;
  entityIdPathParam?: string;
  entityType?: string;
  errorMessage: string;
  filenamePrefix?: string;
  fullPath?: string;
  logName: string;
  loadSuccessResponseFactory?: () => KeyedObject;
  /**
   * Defaults to `'GET'`. `'POST'` routes still serve a fixture - the mock server
   * has no store to write to - but they exercise the mutation path, which is how
   * a page test covers `useMutation` at all.
   */
  method?: EndpointMethod;
  /**
   * Path segments after the entity id, e.g. `['comps']` for
   * `properties/:propertyId/comps`. They also namespace the fixture on disk, so
   * that route's data lives at `properties/comps/<uuid>__data.json.gz`.
   */
  subPath?: string[];
  // requestBodyFallback:
  successStatusMessage?: string;
};

export type MockSuccessResponse<T = any> = MockResponse<T>;
export type MockErrorResponse = {
  detail: string;
  status: number;
};

export type MockResponse<T = any> = MockSuccessResponse<T> | MockErrorResponse;

export type MockResponseCache = KeyedObject<MockResponse | MockErrorResponse>;
