from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import cast

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

# from fastapi_csrf_protect import CsrfProtect
# from fastapi_csrf_protect.exceptions import CsrfProtectError
from pydantic import BaseModel

from api.middlewares.common import add_process_time_header
from constants import window_width
from utils.logging.extended_logger import ExtendedLogger
from utils.logging.init import init_logging

init_logging(app_name="aoam-api")
logger = cast(ExtendedLogger, logging.getLogger(__file__))


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(
        f"\n{'-' * window_width}"
        "\nStarting aoam API server..."
        f"\n{'-' * window_width}"
    )
    yield
    logger.info(
        f"\n{'-' * window_width}"
        "\nShutting down aoam API server..."
        f"\n{'-' * window_width}"
    )


app = FastAPI(lifespan=lifespan)


# NOTE: middleware executed bottom to top
app.middleware("http")(add_process_time_header)


@app.get("/api/health-check")
async def read_health_check():
    return JSONResponse(
        status_code=200, content={"message": "Yaaaaaay, health! Salud!"}
    )
