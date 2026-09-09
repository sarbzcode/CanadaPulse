"""Weekday rates, Friday labour snapshots; manual dispatch can choose either source."""

import os
from datetime import UTC, date, datetime

from canadapulse.config import load_settings
from canadapulse.ingestion.pipelines import initialize, run_source
from canadapulse.logging_config import configure_logging
from canadapulse.services.warehouse_service import refresh_warehouse


def selected_sources(requested: str, weekday: int) -> list[str]:
    if requested not in {"", "all", "boc", "statcan"}:
        raise ValueError("Unknown scheduled source")
    if requested == "all" or (not requested and weekday == 4):
        return ["boc", "statcan"]
    return [requested or "boc"]


def main() -> None:
    if not os.getenv("DATABASE_URL"):
        raise RuntimeError("A production writer DATABASE_URL must be configured")
    settings = load_settings()
    configure_logging(settings.log_level)
    initialize(settings)
    for source in selected_sources(os.getenv("REQUESTED_SOURCE", ""), datetime.now(UTC).weekday()):
        run_source(settings, source, date(2015, 1, 1))
    refresh_warehouse(settings)


if __name__ == "__main__":
    main()
