from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import cast

from fastapi import FastAPI, Request
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi_crons import Crons, get_cron_router

# from fastapi_csrf_protect import CsrfProtect
# from fastapi_csrf_protect.exceptions import CsrfProtectError
from pydantic import BaseModel

from api.middlewares.common import add_process_time_header
from constants import window_width
from utils.logging.extended_logger import ExtendedLogger
from utils.logging.init import init_logging

init_logging(app_name="aoam-api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger = cast(ExtendedLogger, logging.getLogger(__file__))

    divider = "-" * window_width

    logger.info(
        "\n".join(
            [
                divider,
                "Starting aoam API server...",
                divider,
            ]
        )
    )
    yield
    logger.info(
        "\n".join(
            [
                divider,
                "Shutting down aoam API server...",
                divider,
            ]
        )
    )


app = FastAPI(lifespan=lifespan)
crons = Crons(app)

# Ensure cron decorators execute (registration happens at import time)
import api.crons.job_registry  # noqa: E402,F401

app.include_router(
    get_cron_router(),
    # prefix="/api/crons"
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=[
        "healthcheck.railway.app",
        "localhost",
        "aoam-property-plan-production.up.railway.app",
    ],
)


# NOTE: middleware executed bottom to top
app.middleware("http")(add_process_time_header)


@app.get("/api/health-check")
async def read_health_check():
    return JSONResponse(
        status_code=200, content={"message": "Yaaaaaay, health! Salud!"}
    )
