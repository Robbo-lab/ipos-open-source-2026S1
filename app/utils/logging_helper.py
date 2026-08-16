from __future__ import annotations

import inspect
import logging
import logging.config
from functools import wraps
from pathlib import Path
from typing import Any, Callable, TypeVar

F = TypeVar("F", bound=Callable[..., Any])

DEFAULT_LOG_DIR = Path("logs")
DEFAULT_LOG_FILE = DEFAULT_LOG_DIR / "mcp_log_streamable_http.log"
DEFAULT_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"


def build_log_config(
    log_file: Path,
    logger_handlers: dict[str, list[str]] | None = None,
    root_level: str = "INFO",
    logger_level: str = "DEBUG",
) -> dict[str, Any]:
    """Build a `logging.config.dictConfig` layout for centralised file logging."""
    log_file = Path(log_file)
    if not log_file.is_absolute():
        log_file = DEFAULT_LOG_DIR / log_file

    log_file.parent.mkdir(parents=True, exist_ok=True)

    handlers = {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "level": logger_level,
            "stream": "ext://sys.stdout",
        },
        "rotating_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "default",
            "level": logger_level,
            "filename": str(log_file),
            "mode": "a",
            "maxBytes": 10_485_760,
            "backupCount": 5,
            "encoding": "utf-8",
        },
    }

    loggers: dict[str, Any] = {}
    if logger_handlers:
        for logger_name, handler_names in logger_handlers.items():
            loggers[logger_name] = {
                "level": logger_level,
                "handlers": handler_names,
                "propagate": False,
            }

    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": DEFAULT_FORMAT,
            }
        },
        "handlers": handlers,
        "root": {
            "level": root_level,
            "handlers": ["console", "rotating_file"],
        },
        "loggers": loggers,
    }


def setup_logging(
    log_file: Path | str = DEFAULT_LOG_FILE,
    logger_handlers: dict[str, list[str]] | None = None,
    root_level: str = "INFO",
    logger_level: str = "DEBUG",
) -> None:
    """Configure Python logging using a shared central log directory."""
    if isinstance(log_file, str):
        log_file = Path(log_file)
    config = build_log_config(
        log_file,
        logger_handlers=logger_handlers,
        root_level=root_level,
        logger_level=logger_level,
    )
    logging.config.dictConfig(config)


def log_decorator(
    logger_name: str = "app",
    level: str = "INFO",
) -> Callable[[F], F]:
    """Create a decorator that logs calls and exceptions for a function.
    
    Uses the centralized logging configuration setup via setup_logging().
    Handles both sync and async functions.
    """
    level_value = getattr(logging, level.upper(), logging.INFO)

    def decorator(func: F) -> F:
        logger = logging.getLogger(logger_name)
        logger.setLevel(level_value)

        if inspect.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                logger.log(
                    level_value,
                    "Calling %s with args=%s kwargs=%s",
                    func.__name__,
                    args,
                    kwargs,
                )
                try:
                    result = await func(*args, **kwargs)
                    logger.log(level_value, "%s completed successfully", func.__name__)
                    return result
                except Exception:  # pragma: no cover
                    logger.exception("Exception in %s", func.__name__)
                    raise
            return async_wrapper
        else:
            @wraps(func)
            def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
                logger.log(
                    level_value,
                    "Calling %s with args=%s kwargs=%s",
                    func.__name__,
                    args,
                    kwargs,
                )
                try:
                    result = func(*args, **kwargs)
                    logger.log(level_value, "%s completed successfully", func.__name__)
                    return result
                except Exception:  # pragma: no cover
                    logger.exception("Exception in %s", func.__name__)
                    raise
            return sync_wrapper

    return decorator
