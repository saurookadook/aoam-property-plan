import type { KeyedObject, MockSuccessResponse, MockErrorResponse } from '@/types';

export function create200Response<T = any>(
  result: T, // force formatting
) {
  return {
    data: result,
  };
}

export function createErrorResponse(errorDetail: string): MockErrorResponse {
  return {
    detail: errorDetail,
  };
}

export function create400Response(
  errorDetail: string = 'Bad request', // force formatting
) {
  return createErrorResponse(errorDetail);
}

export function create500Response(
  errorDetail: string = 'Internal server error', // force formatting
) {
  return createErrorResponse(errorDetail);
}
