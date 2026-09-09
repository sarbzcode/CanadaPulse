"""Thin service layer for pipeline status checks."""

from __future__ import annotations

from dataclasses import dataclass

from canadapulse.config import AppSettings
from canadapulse.database.connection import DatabaseHealth, check_database


@dataclass(frozen=True)
class ApplicationStatus:
    """Current application status for CLI and future API health endpoints."""

    service_version: str
    environment: str
    database: DatabaseHealth


class PipelineService:
    """Coordinate cross-cutting pipeline operations."""

    def __init__(self, settings: AppSettings) -> None:
        self._settings = settings

    def status(self) -> ApplicationStatus:
        """Return runtime status."""

        return ApplicationStatus(
            service_version=self._settings.service_version,
            environment=self._settings.environment,
            database=check_database(self._settings.database),
        )

