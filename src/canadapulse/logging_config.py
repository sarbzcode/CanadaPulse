"""Application logging configuration."""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from typing import Any


class JsonFormatter(logging.Formatter):
    """Small JSON formatter that keeps logs machine-readable in containers."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for attr in (
            "pipeline_run_id",
            "source_name",
            "table_name",
            "records_loaded",
            "records_inserted",
            "records_updated",
            "records_unchanged",
            "bytes_downloaded",
        ):
            value = getattr(record, attr, None)
            if value is not None:
                payload[attr] = value
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


def configure_logging(level: str = "INFO", *, json_logs: bool = True) -> None:
    """Configure root logging once for CLI, jobs, and future API runtime."""

    formatter: logging.Formatter
    if json_logs:
        formatter = JsonFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s %(levelname)s [%(name)s] %(message)s",
        )

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logging.basicConfig(level=level.upper(), handlers=[handler], force=True)


def get_logger(name: str) -> logging.Logger:
    """Return a named logger."""

    return logging.getLogger(name)
