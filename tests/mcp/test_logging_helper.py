import logging
from pathlib import Path

from app.utils.logging_helper import build_log_config, log_decorator, setup_logging


def test_build_log_config_creates_rotating_file(tmp_path: Path) -> None:
    log_file = tmp_path / "logs" / "mcp_log_streamable_http.log"
    config = build_log_config(
        log_file,
        logger_handlers={"uvicorn": ["rotating_file", "console"]},
        root_level="INFO",
        logger_level="DEBUG",
    )

    assert config["handlers"]["rotating_file"]["filename"] == str(log_file)
    assert config["loggers"]["uvicorn"]["handlers"] == ["rotating_file", "console"]
    assert log_file.parent.exists()


def test_log_decorator_writes_log_entries(tmp_path: Path) -> None:
    log_file = tmp_path / "logs" / "decorated.log"
    setup_logging(
        log_file,
        logger_handlers={"custom": ["rotating_file"]},
        root_level="INFO",
        logger_level="INFO",
    )

    @log_decorator(logger_name="custom", level="INFO", filename=log_file)
    def sample(a: int, b: int) -> int:
        return a + b

    expected_result = 5
    assert sample(2, 3) == expected_result

    text = log_file.read_text(encoding="utf-8")
    assert "Calling sample" in text
    assert "sample completed successfully" in text

    logger = logging.getLogger("custom")
    for handler in list(logger.handlers):
        logger.removeHandler(handler)
