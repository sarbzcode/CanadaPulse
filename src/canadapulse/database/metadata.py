"""Pipeline run metadata persistence."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from canadapulse.exceptions import PipelineMetadataError


class PipelineRunStatus(StrEnum):
    """Allowed metadata.pipeline_runs statuses."""

    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    PARTIAL = "PARTIAL"


@dataclass(frozen=True)
class PipelineRunCounts:
    """Observed row counts for an ingestion pipeline run."""

    records_extracted: int = 0
    records_loaded: int = 0
    records_rejected: int = 0

    def __post_init__(self) -> None:
        for field_name in ("records_extracted", "records_loaded", "records_rejected"):
            if getattr(self, field_name) < 0:
                raise PipelineMetadataError(f"{field_name} must be non-negative.")


class PipelineRunRepository:
    """Write pipeline lifecycle information to PostgreSQL."""

    def __init__(self, connection: Any) -> None:
        self._connection = connection

    def start_run(self, pipeline_name: str, source_name: str) -> UUID:
        """Create a RUNNING metadata row and return its pipeline_run_id."""

        if not pipeline_name:
            raise PipelineMetadataError("pipeline_name must not be empty.")
        if not source_name:
            raise PipelineMetadataError("source_name must not be empty.")

        pipeline_run_id = uuid4()
        started_at = datetime.now(UTC)
        try:
            with self._connection.cursor() as cursor:
                cursor.execute(
                    """
                    insert into metadata.pipeline_runs (
                        pipeline_run_id,
                        pipeline_name,
                        source_name,
                        started_at,
                        status
                    )
                    values (%s, %s, %s, %s, %s)
                    """,
                    (
                        pipeline_run_id,
                        pipeline_name,
                        source_name,
                        started_at,
                        PipelineRunStatus.RUNNING.value,
                    ),
                )
            self._connection.commit()
        except Exception as exc:
            self._connection.rollback()
            raise PipelineMetadataError("Failed to create pipeline metadata row.") from exc
        return pipeline_run_id

    def complete_run(
        self,
        pipeline_run_id: UUID,
        *,
        status: PipelineRunStatus = PipelineRunStatus.SUCCESS,
        counts: PipelineRunCounts,
        error_message: str | None = None,
    ) -> None:
        """Mark a pipeline run complete with observed counts."""

        if status is PipelineRunStatus.RUNNING:
            raise PipelineMetadataError("complete_run cannot set status to RUNNING.")

        completed_at = datetime.now(UTC)
        try:
            with self._connection.cursor() as cursor:
                cursor.execute(
                    """
                    update metadata.pipeline_runs
                    set
                        completed_at = %s,
                        status = %s,
                        records_extracted = %s,
                        records_loaded = %s,
                        records_rejected = %s,
                        duration_seconds = extract(epoch from (%s - started_at)),
                        error_message = %s,
                        updated_at = now()
                    where pipeline_run_id = %s
                    """,
                    (
                        completed_at,
                        status.value,
                        counts.records_extracted,
                        counts.records_loaded,
                        counts.records_rejected,
                        completed_at,
                        error_message,
                        pipeline_run_id,
                    ),
                )
                if cursor.rowcount != 1:
                    raise PipelineMetadataError(
                        f"Pipeline run {pipeline_run_id} does not exist.",
                    )
            self._connection.commit()
        except PipelineMetadataError:
            self._connection.rollback()
            raise
        except Exception as exc:
            self._connection.rollback()
            raise PipelineMetadataError("Failed to update pipeline metadata row.") from exc

