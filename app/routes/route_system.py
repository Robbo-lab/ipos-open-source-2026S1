import datetime
import os
import platform
import time

from app.routes.router_handler import Router
from app.utils.response_helper import build_success_response

system_router = Router.get_router("system")

started_at = time.time()


@system_router.get("/")
def root():
    return build_success_response({
        "service": "unit-converter-mcp-server",
        "status": "ok",
        "docs": "/docs",
        "health": "/health",
        "mcp": "/mcp/",
    })


@system_router.get("/health")
def health():
    return build_success_response({
        "status": "ok",
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat() + "Z",
        "python": platform.python_version(),
        "platform": platform.platform(),
        "pid": os.getpid(),
        "cwd": os.getcwd(),
        "uptime_seconds": round(time.time() - started_at, 2),
    })
