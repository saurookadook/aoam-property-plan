/**
 * Unwraps the API's `{ data: ... }` envelope, throwing on a non-2xx response.
 *
 * `fetchy` resolves for every status the server actually answers with, so
 * `fetchy.get(...).then((res) => res.json())` hands react-query a 500's
 * `{ detail: ... }` body as a *success* whose `data` is `undefined`. That is why
 * `MarketsList` renders an empty grid and no toast when the backend is down: the
 * query never enters its error state, so `error` stays `null` and there is
 * nothing to show a toast for.
 *
 * Every read in the app goes through here so that a failure is a rejected
 * promise - the one thing react-query's `error`, `isError` and retry behaviour
 * all key off.
 */
export class ApiError extends Error {
  readonly status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

const FALLBACK_MESSAGE = 'The server returned an unexpected response.';

export async function unwrapEnvelope<T>(response: Response): Promise<T> {
  const body = await readJsonBody(response);

  if (!response.ok) {
    throw new ApiError(resolveErrorMessage(body, response), response.status);
  }

  if (body == null || typeof body !== 'object' || !('data' in body)) {
    throw new ApiError(FALLBACK_MESSAGE, response.status);
  }

  return (body as { data: T }).data;
}

/**
 * A body that is not JSON is itself the failure worth reporting, so this returns
 * `null` rather than throwing and lets the caller decide which message applies.
 */
async function readJsonBody(response: Response): Promise<unknown> {
  try {
    return await response.json();
  } catch {
    return null;
  }
}

/**
 * FastAPI's error shape is `{ detail: ... }`, where `detail` is a string for a
 * raised `HTTPException` and a list of per-field objects for a 422. Both are
 * rendered rather than only the first, because a 422 that says nothing about
 * which field failed is indistinguishable from a bug in the client.
 */
function resolveErrorMessage(body: unknown, response: Response): string {
  const statusText = `${response.status}${response.statusText ? ` ${response.statusText}` : ''}`;

  if (body == null || typeof body !== 'object' || !('detail' in body)) {
    return `Request failed (${statusText}).`;
  }

  const { detail } = body as { detail: unknown };

  if (typeof detail === 'string' && detail !== '') {
    return detail;
  }

  if (Array.isArray(detail)) {
    const messages = detail
      .map((entry) => formatValidationEntry(entry))
      .filter((message): message is string => message != null);

    if (messages.length > 0) {
      return messages.join('; ');
    }
  }

  return `Request failed (${statusText}).`;
}

function formatValidationEntry(entry: unknown): string | null {
  if (entry == null || typeof entry !== 'object') {
    return null;
  }

  const { loc, msg } = entry as { loc?: unknown; msg?: unknown };

  if (typeof msg !== 'string') {
    return null;
  }

  if (!Array.isArray(loc) || loc.length === 0) {
    return msg;
  }

  // `loc` leads with the source ("body", "query"), which tells the user nothing.
  const field = loc.slice(1).join('.') || String(loc[0]);

  return `${field}: ${msg}`;
}
