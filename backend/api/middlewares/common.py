from __future__ import annotations

from collections.abc import Awaitable
from time import time_ns
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

NextFunc = Callable[[Request], Awaitable[Response]]


async def add_process_time_header(request: Request, call_next: NextFunc) -> Response:
    start_time = time_ns()
    response: Response = await call_next(request)
    process_time = time_ns() - start_time
    response.headers["X-Process-Time"] = str(process_time / 1_000_000) + " ms"
    return response


# -------------------------- NOTE --------------------------
# alternative approach to writing middleware
# - see: https://stackoverflow.com/questions/71525132/how-to-write-a-custom-fastapi-middleware-class
#
# ----------------------------------------------------------
class CommonMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, **kwargs):
        super().__init__(app, **kwargs)

    async def dispatch(self, request: Request, call_next: Callable):
        response = await add_process_time_header(request, call_next)
        return response
