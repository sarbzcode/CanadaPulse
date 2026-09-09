from __future__ import annotations

import os
from pathlib import Path

import pytest

from canadapulse.config import DatabaseSettings, load_env_file, load_settings
from canadapulse.exceptions import ConfigurationError


@pytest.fixture(autouse=True)
def isolated_configuration_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep fixture precedence independent of developer and CI database settings."""
    for name in tuple(os.environ):
        if name.startswith("CANADAPULSE_") or name in {
            "DATABASE_URL", "ENVIRONMENT", "CORS_ORIGINS", "API_HOST", "API_PORT"
        }:
            monkeypatch.delenv(name)


def test_database_settings_redacts_password() -> None:
    settings = DatabaseSettings(
        host="localhost",
        port=5432,
        database="canadapulse",
        user="canadapulse",
        password="local-password",
        sslmode="disable",
        connect_timeout_seconds=5,
    )

    assert settings.redacted()["password"] == "***"
    assert settings.as_connection_kwargs()["password"] == "local-password"


def test_load_settings_reads_dotenv_without_overriding_existing_env(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "CANADAPULSE_ENV=from-file",
                "CANADAPULSE_LOG_LEVEL=debug",
                "CANADAPULSE_DB_HOST=db",
                "CANADAPULSE_DB_PORT=5544",
                "CANADAPULSE_DB_NAME=warehouse",
                "CANADAPULSE_DB_USER=loader",
                "CANADAPULSE_DB_PASSWORD=file-password",
            ],
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("CANADAPULSE_ENV", "from-process")

    settings = load_settings(env_file=env_file)

    assert settings.environment == "from-process"
    assert settings.log_level == "DEBUG"
    assert settings.database.host == "db"
    assert settings.database.port == 5544
    assert settings.database.password == "file-password"


def test_invalid_port_raises_configuration_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CANADAPULSE_DB_PORT", "not-a-port")

    with pytest.raises(ConfigurationError, match="CANADAPULSE_DB_PORT"):
        load_settings(env_file=None)


def test_invalid_dotenv_line_raises_configuration_error(tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("CANADAPULSE_ENV\n", encoding="utf-8")

    with pytest.raises(ConfigurationError, match="Invalid dotenv entry"):
        load_env_file(env_file)


def test_database_url_decodes_credentials_and_requires_tls(monkeypatch):
    monkeypatch.setenv(
        "DATABASE_URL", "postgresql://reader:p%40ss@db.example.org/platform?sslmode=require"
    )
    monkeypatch.setenv("ENVIRONMENT", "production")
    settings = load_settings(None)
    assert settings.database.password == "p@ss"
    assert settings.database.host == "db.example.org"
    assert settings.database.port == 5432
    assert settings.database.sslmode == "require"
    assert "p@ss" not in str(settings.redacted())


def test_bad_url_does_not_disclose_secret(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "https://private-secret")
    with pytest.raises(ConfigurationError) as error:
        load_settings(None)
    assert "private-secret" not in str(error.value)


def test_production_rejects_wildcard_cors(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("CORS_ORIGINS", "*")
    with pytest.raises(ConfigurationError, match="CORS"):
        load_settings(None)
