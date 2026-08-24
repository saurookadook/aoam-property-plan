import type { KeyedObject, MockSuccessResponse, MockErrorResponse } from '@/types';

export function create200Response<T = any>(
  result: T, // force formatting
) {
  return {
    data: result,
  };
}

export function createErrorResponse(
  errorDetail: string,
  statusCode: number,
): MockErrorResponse {
  return {
    detail: errorDetail,
    status: statusCode,
  };
}

export function create400Response(
  errorDetail: string = 'Bad request', // force formatting
) {
  return createErrorResponse(errorDetail, 400);
}

export function create500Response(
  errorDetail: string = 'Internal server error', // force formatting
) {
  return createErrorResponse(errorDetail, 500);
}
