import os
import multiprocessing

workers = int(os.getenv("WORKERS", 1))
loglevel = os.getenv("LOG_LEVEL", "warning")
host = os.getenv("HOST", "0.0.0.0")
port = os.getenv("PORT", "3000")
bind = f"{host}:{port}"

keepalive = int(os.getenv("KEEPALIVE", 24 * 60 * 60))  # 1 day
timeout = int(os.getenv("TIMEOUT", 60))  # 1 minute
reload = os.getenv("RELOAD", "false").lower() in ("true", "1", "yes")
reload_engine = "poll"

worker_class = "uvicorn.workers.UvicornWorker"
