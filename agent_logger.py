
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "agent_execution.log"


def setup_logger():
    logger = logging.getLogger("voice_agent")
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler = RotatingFileHandler(
            LOG_FILE,
            maxBytes=1_000_000,
            backupCount=3,
            encoding="utf-8"
        )

        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(message)s"
        )

        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.propagate = False
    return logger


agent_logger = setup_logger()


def log_tool_execution(tool_name, success, duration_ms):
    """
    Record tool execution metadata.

    Do not log note contents, task descriptions,
    API keys, or other private user input.
    """

    status = "SUCCESS" if success else "FAILED"

    agent_logger.info(
        "tool=%s | status=%s | duration_ms=%.2f",
        tool_name,
        status,
        duration_ms
    )
