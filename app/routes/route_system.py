import datetime
import os
import platform
import time
from pathlib import Path

from app.routes.router_handler import Router
from app.utils.logging_helper import log_decorator

system_router = Router.get_router("system")

started_at = time.time()


@system_router.get("/")
@log_decorator(
    logger_name="rest.system.root",
    level="INFO",
    filename=Path("rest_root.log"),
)
def root():
    return {
        "service": "unit-converter-mcp-server",
        "status": "ok",
        "docs": "/docs",
        "health": "/health",
        "mcp": "/mcp/",
    }


@system_router.get("/health")
@log_decorator(
    logger_name="rest.system.health",
    level="INFO",
    filename=Path("rest_health.log"),
)
def health():
    return {
        "status": "ok",
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat() + "Z",
        "python": platform.python_version(),
        "platform": platform.platform(),
        "pid": os.getpid(),
        "cwd": os.getcwd(),
        "uptime_seconds": round(time.time() - started_at, 2),
    }
