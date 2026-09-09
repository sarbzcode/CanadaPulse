"""Runtime configuration loaded from environment variables."""

from __future__ import annotations

from dataclasses import dataclass
from os import environ
from pathlib import Path

from canadapulse.exceptions import ConfigurationError

DEFAULT_ENV_FILE = Path(".env")
ALLOWED_LOG_LEVELS = {"CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"}
ALLOWED_SSL_MODES = {"disable", "allow", "prefer", "require", "verify-ca", "verify-full"}


@dataclass(frozen=True)
class DatabaseSettings:
    """PostgreSQL connection settings."""

    host: str
    port: int
    database: str
    user: str
    password: str | None
    sslmode: str
    connect_timeout_seconds: int

    def __post_init__(self) -> None:
        if not self.host:
            raise ConfigurationError("CANADAPULSE_DB_HOST must not be empty.")
        if not 1 <= self.port <= 65535:
            raise ConfigurationError("CANADAPULSE_DB_PORT must be between 1 and 65535.")
        if not self.database:
            raise ConfigurationError("CANADAPULSE_DB_NAME must not be empty.")
        if not self.user:
            raise ConfigurationError("CANADAPULSE_DB_USER must not be empty.")
        if self.sslmode not in ALLOWED_SSL_MODES:
            allowed = ", ".join(sorted(ALLOWED_SSL_MODES))
            raise ConfigurationError(f"CANADAPULSE_DB_SSLMODE must be one of: {allowed}.")
        if self.connect_timeout_seconds <= 0:
            raise ConfigurationError("CANADAPULSE_DB_CONNECT_TIMEOUT_SECONDS must be positive.")

    def as_connection_kwargs(self) -> dict[str, object]:
        """Return kwargs accepted by psycopg.connect."""

        kwargs: dict[str, object] = {
            "host": self.host,
            "port": self.port,
            "dbname": self.database,
            "user": self.user,
            "sslmode": self.sslmode,
            "connect_timeout": self.connect_timeout_seconds,
        }
        if self.password:
            kwargs["password"] = self.password
        return kwargs

    def redacted(self) -> dict[str, object]:
        """Return settings safe to print in logs or CLI output."""

        return {
            "host": self.host,
            "port": self.port,
            "database": self.database,
            "user": self.user,
            "password": "***" if self.password else None,
            "sslmode": self.sslmode,
            "connect_timeout_seconds": self.connect_timeout_seconds,
        }


@dataclass(frozen=True)
class AppSettings:
    """Top-level application settings."""

    environment: str
    log_level: str
    service_version: str
    database: DatabaseSettings

    def __post_init__(self) -> None:
        if not self.environment:
            raise ConfigurationError("CANADAPULSE_ENV must not be empty.")
        if self.log_level not in ALLOWED_LOG_LEVELS:
            allowed = ", ".join(sorted(ALLOWED_LOG_LEVELS))
            raise ConfigurationError(f"CANADAPULSE_LOG_LEVEL must be one of: {allowed}.")
        if not self.service_version:
            raise ConfigurationError("CANADAPULSE_SERVICE_VERSION must not be empty.")

    def redacted(self) -> dict[str, object]:
        """Return settings safe to display."""

        return {
            "environment": self.environment,
            "log_level": self.log_level,
            "service_version": self.service_version,
            "database": self.database.redacted(),
        }


def load_env_file(path: Path = DEFAULT_ENV_FILE) -> dict[str, str]:
    """Parse simple KEY=VALUE pairs from a dotenv file."""

    if not path.exists():
        return {}

    values: dict[str, str] = {}
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise ConfigurationError(f"Invalid dotenv entry at {path}:{line_number}.")
        key, value = line.split("=", 1)
        key = key.strip()
        if not key:
            raise ConfigurationError(f"Invalid empty dotenv key at {path}:{line_number}.")
        values[key] = _clean_env_value(value)
    return values


def load_settings(env_file: Path | None = DEFAULT_ENV_FILE) -> AppSettings:
    """Load and validate CanadaPulse settings."""

    file_env = load_env_file(env_file) if env_file is not None else {}

    database = DatabaseSettings(
        host=_get_env("CANADAPULSE_DB_HOST", default="localhost", file_env=file_env),
        port=_get_int_env("CANADAPULSE_DB_PORT", default=55432, file_env=file_env),
        database=_get_env("CANADAPULSE_DB_NAME", default="canadapulse", file_env=file_env),
        user=_get_env("CANADAPULSE_DB_USER", default="canadapulse", file_env=file_env),
        password=_get_optional_env("CANADAPULSE_DB_PASSWORD", file_env=file_env),
        sslmode=_get_env("CANADAPULSE_DB_SSLMODE", default="disable", file_env=file_env),
        connect_timeout_seconds=_get_int_env(
            "CANADAPULSE_DB_CONNECT_TIMEOUT_SECONDS",
            default=5,
            file_env=file_env,
        ),
    )
    return AppSettings(
        environment=_get_env("CANADAPULSE_ENV", default="local", file_env=file_env),
        log_level=_get_env("CANADAPULSE_LOG_LEVEL", default="INFO", file_env=file_env).upper(),
        service_version=_get_env(
            "CANADAPULSE_SERVICE_VERSION",
            default="0.1.0",
            file_env=file_env,
        ),
        database=database,
    )


def _clean_env_value(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def _get_env(name: str, *, default: str, file_env: dict[str, str]) -> str:
    value = _get_raw_value(name, default=default, file_env=file_env).strip()
    if not value:
        raise ConfigurationError(f"{name} must not be empty.")
    return value


def _get_optional_env(name: str, *, file_env: dict[str, str]) -> str | None:
    value = _get_raw_value(name, default=None, file_env=file_env)
    if value is None:
        return None
    value = value.strip()
    return value or None


def _get_int_env(name: str, *, default: int, file_env: dict[str, str]) -> int:
    value = _get_raw_value(name, default=None, file_env=file_env)
    if value is None or not value.strip():
        return default
    try:
        return int(value)
    except ValueError as exc:
        raise ConfigurationError(f"{name} must be an integer.") from exc


def _get_raw_value(name: str, *, default: str | None, file_env: dict[str, str]) -> str | None:
    return environ.get(name, file_env.get(name, default))
