import { type Request } from 'express';

export function logRouteHandlerStart(request: Request) {
  console.log('-'.repeat(120));
  console.log(`[${request.originalUrl}] In router: `);
  console.log({
    reqBody: request.body,
    reqBodyType: typeof request.body,
    reqHeaders: request.headers,
    reqRawHeaders: request.rawHeaders,
  });
  console.log('-'.repeat(120));
}
