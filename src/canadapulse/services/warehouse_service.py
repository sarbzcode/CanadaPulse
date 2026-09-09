"""Run dbt using the same validated settings as ingestion; no credentials on argv."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from psycopg.types.json import Jsonb

from canadapulse.config import AppSettings, load_settings
from canadapulse.database.connection import connect
from canadapulse.database.metadata import (
    PipelineRunCounts,
    PipelineRunRepository,
    PipelineRunStatus,
)

ROOT = Path(__file__).resolve().parents[3]


def configure_dbt_environment(settings: AppSettings) -> None:
    database = settings.database
    os.environ.update(
        {
            "DBT_HOST": database.host,
            "DBT_PORT": str(database.port),
            "DBT_USER": database.user,
            "DBT_ENV_SECRET_PASSWORD": database.password or "",
            "DBT_DATABASE": database.database,
            "DBT_SSLMODE": database.sslmode,
            "DBT_SEND_ANONYMOUS_USAGE_STATS": "false",
        }
    )


def run_dbt(args: list[str], settings: AppSettings | None = None) -> None:
    """CLI-compatible dbt invocation, failing the calling pipeline on any failed test."""
    from dbt.cli.main import dbtRunner

    configure_dbt_environment(settings or load_settings())
    result = dbtRunner().invoke(
        [
            *args,
            "--project-dir",
            str(ROOT / "warehouse"),
            "--profiles-dir",
            str(ROOT / "warehouse"),
        ]
    )
    if not result.success:
        raise RuntimeError(
            "dbt command failed; inspect the dbt logs for details"
        ) from result.exception


def refresh_warehouse(settings: AppSettings | None = None) -> dict[str, Any]:
    """Build and test the warehouse, recording actual dbt outcomes and served row counts."""
    settings = settings or load_settings()
    with connect(settings.database) as connection:
        connection.execute("SELECT pg_advisory_lock(hashtext('canadapulse:warehouse'))")
        repository = PipelineRunRepository(connection)
        run_id = repository.start_run("dbt_build", "warehouse")
        artifact = ROOT / "warehouse/target/run_results.json"
        artifact.unlink(missing_ok=True)
        failure = None
        try:
            run_dbt(["build"], settings)
        except Exception as exc:
            failure = exc
        if artifact.exists():
            result = json.loads(artifact.read_text(encoding="utf-8"))
            for item in result.get("results", []):
                if not item["unique_id"].startswith("test."):
                    continue
                status = "PASS" if item["status"] == "pass" else "FAIL"
                connection.execute(
                    "INSERT INTO metadata.data_quality_results "
                    "(pipeline_run_id, check_name, table_name, status, observed_value, "
                    "expected_condition) VALUES (%s,%s,'warehouse',%s,%s,%s)",
                    (
                        run_id,
                        item["unique_id"],
                        status,
                        Jsonb({"failing_rows": item.get("failures"), "status": item["status"]}),
                        "dbt assertion passes with zero failing rows",
                    ),
                )
            connection.commit()
        if failure:
            repository.complete_run(
                run_id,
                status=PipelineRunStatus.FAILED,
                counts=PipelineRunCounts(),
                error_message="dbt build failed",
            )
            raise failure
        rows = connection.execute(
            "SELECT (SELECT count(*) FROM warehouse.fact_labour_market) + "
            "(SELECT count(*) FROM warehouse.fact_interest_rates)"
        ).fetchone()[0]
        repository.complete_run(run_id, counts=PipelineRunCounts(rows, rows))
        return {"run_id": str(run_id), "warehouse_records": rows}


if __name__ == "__main__":
    import sys

    if sys.argv[1:] == ["refresh"]:
        print(refresh_warehouse())
    else:
        run_dbt(sys.argv[1:] or ["build"])
