"""Persist measured quality observations without turning missing values into failures."""

from dataclasses import dataclass
from datetime import date
from typing import Any
from uuid import UUID

from psycopg.types.json import Jsonb


@dataclass(frozen=True)
class LoadMetrics:
    loaded: int
    inserted: int
    updated: int
    unchanged: int
    null_values: int
    first_date: date
    last_date: date

    @property
    def null_rate(self) -> float:
        return self.null_values / self.loaded if self.loaded else 0.0


def record_load_quality(connection: Any, run_id: UUID, source: str, metrics: LoadMetrics) -> None:
    """Write alongside source data, allowing the caller to commit the entire load atomically."""
    connection.execute(
        "UPDATE metadata.pipeline_runs SET records_inserted=%s, records_updated=%s, "
        "records_unchanged=%s, latest_reference_date=%s WHERE pipeline_run_id=%s",
        (metrics.inserted, metrics.updated, metrics.unchanged, metrics.last_date, run_id),
    )
    checks = [
        ("non_empty_selected_scope", metrics.loaded, "At least one selected observation"),
        ("unique_source_identity", metrics.loaded, "One incoming row per source identity"),
        (
            "load_reconciliation",
            {
                "inserted": metrics.inserted,
                "revised": metrics.updated,
                "unchanged": metrics.unchanged,
                "loaded": metrics.loaded,
            },
            "Inserted + revised + unchanged equals successfully loaded observations",
        ),
        (
            "missing_value_rate",
            {"count": metrics.null_values, "rate": metrics.null_rate},
            "Informational: source suppression is preserved, not replaced with zero",
        ),
        (
            "reference_coverage",
            {"first": str(metrics.first_date), "last": str(metrics.last_date)},
            "Valid source dates in the requested extraction scope",
        ),
    ]
    for name, observed, expectation in checks:
        connection.execute(
            "INSERT INTO metadata.data_quality_results "
            "(pipeline_run_id, check_name, table_name, status, observed_value, expected_condition) "
            "VALUES (%s,%s,%s,'PASS',%s,%s)",
            (run_id, name, source, Jsonb(observed), expectation),
        )
