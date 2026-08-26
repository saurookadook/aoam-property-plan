import { describe, expect, it } from 'vitest';

import { ApiError, unwrapEnvelope } from '@/utils';

function jsonResponse(body: unknown, init?: ResponseInit): Response {
  return new Response(JSON.stringify(body), {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  });
}

describe('unwrapEnvelope', () => {
  it('returns the payload nested under `data`', async () => {
    const response = jsonResponse({ data: [{ id: 'abc' }] });

    await expect(unwrapEnvelope<{ id: string }[]>(response)).resolves.toEqual([
      { id: 'abc' },
    ]);
  });

  it('returns a null payload rather than treating it as a failure', async () => {
    // `GET /properties/{id}/report` answers `{"data": null}` with a 200 for a
    // property that has never been analysed. That is an answer, not an error.
    await expect(unwrapEnvelope(jsonResponse({ data: null }))).resolves.toBeNull();
  });

  it('rejects on a non-2xx response instead of resolving with `undefined`', async () => {
    // The bug this exists for: `.then((res) => res.json())` resolved here, so
    // react-query recorded a success whose `data` was `undefined` - no error, no
    // toast, and an empty grid.
    const response = jsonResponse(
      { detail: 'Error fetching markets' },
      { status: 500 },
    );

    await expect(unwrapEnvelope(response)).rejects.toThrow('Error fetching markets');
  });

  it('carries the status code on the thrown error', async () => {
    const response = jsonResponse({ detail: 'Market not found' }, { status: 404 });

    await expect(unwrapEnvelope(response)).rejects.toMatchObject({
      name: 'ApiError',
      status: 404,
    });
  });

  it("renders FastAPI's per-field 422 detail", async () => {
    const response = jsonResponse(
      {
        detail: [
          {
            loc: ['body', 'interest_rate'],
            msg: 'Extra inputs are not permitted',
            type: 'extra_forbidden',
          },
        ],
      },
      { status: 422 },
    );

    await expect(unwrapEnvelope(response)).rejects.toThrow(
      'interest_rate: Extra inputs are not permitted',
    );
  });

  it('falls back to the status when the body carries no detail', async () => {
    const response = jsonResponse({}, { status: 503 });

    await expect(unwrapEnvelope(response)).rejects.toThrow('503');
  });

  it('rejects when a 2xx body has no envelope at all', async () => {
    const response = new Response('<html>gateway</html>', { status: 200 });

    await expect(unwrapEnvelope(response)).rejects.toBeInstanceOf(ApiError);
  });
});
