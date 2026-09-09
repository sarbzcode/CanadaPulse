"""PostgreSQL connection and health-check utilities."""

from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Any

from canadapulse.config import DatabaseSettings
from canadapulse.exceptions import DatabaseConnectionError


@dataclass(frozen=True)
class DatabaseHealth:
    """Result of a database health check."""

    ok: bool
    message: str
    latency_ms: float | None = None


def connect(settings: DatabaseSettings) -> Any:
    """Create a PostgreSQL connection using psycopg."""

    try:
        import psycopg
    except ImportError as exc:
        raise DatabaseConnectionError(
            "psycopg is not installed. Run `python -m pip install -r requirements.txt`.",
        ) from exc

    try:
        return psycopg.connect(**settings.as_connection_kwargs())
    except Exception as exc:
        raise DatabaseConnectionError(f"Unable to connect to PostgreSQL: {exc}") from exc


def check_database(settings: DatabaseSettings) -> DatabaseHealth:
    """Check whether PostgreSQL is reachable and accepting a trivial query."""

    started_at = perf_counter()
    try:
        with connect(settings) as connection, connection.cursor() as cursor:
            cursor.execute("select 1")
            cursor.fetchone()
    except DatabaseConnectionError as exc:
        return DatabaseHealth(ok=False, message=str(exc))

    latency_ms = round((perf_counter() - started_at) * 1000, 2)
    return DatabaseHealth(ok=True, message="database connection ok", latency_ms=latency_ms)

