from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi_crons import Crons, get_cron_router

# from fastapi_csrf_protect import CsrfProtect
# from fastapi_csrf_protect.exceptions import CsrfProtectError

from api.middlewares.common import add_process_time_header
from api.routes.exchange_rate import exchange_rate_router
from api.routes.home import home_router
from api.routes.listings import listings_router
from api.routes.markets import markets_router
from api.routes.properties import properties_router
from constants import window_width
from utils.logging.init import init_logging, is_prod

logger = init_logging(app_name="aoam-api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    global logger

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


@app.get("/api/health-check")
async def read_health_check():
    return JSONResponse(
        status_code=200, content={"message": "Yaaaaaay, health! Salud!"}
    )


if is_prod():
    # Ensure cron decorators execute (registration happens at import time)
    import api.crons.job_registry  # noqa: E402,F401

app.include_router(
    get_cron_router(),
    # prefix="/api/crons"
)

headers = ["*"]

hosts = [
    "healthcheck.railway.app",
    "aoam-property-plan-production.up.railway.app",
    "aoam-frontend-app-production.up.railway.app",
    # Dev
    "localhost",
    "aoam.dev",
]

methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]

origins = [
    "https://aoam-frontend-app-production.up.railway.app",
]


# NOTE: middleware executed bottom to top
app.middleware("http")(add_process_time_header)


app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=hosts,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=methods,
    allow_headers=headers,
)

app.include_router(home_router)
app.include_router(exchange_rate_router)
app.include_router(listings_router)
app.include_router(markets_router)
app.include_router(properties_router)
