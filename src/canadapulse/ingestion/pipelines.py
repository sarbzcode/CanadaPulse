"""Public-source ingestion with atomic, revision-aware loads and run tracking."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import logging
import shutil
import time
import urllib.error
import urllib.request
import zipfile
from datetime import date
from decimal import Decimal
from pathlib import Path

import yaml
from psycopg import sql
from psycopg.types.json import Jsonb

from canadapulse.database.connection import connect
from canadapulse.database.loader import execute_sql_files
from canadapulse.database.metadata import (
    PipelineRunCounts,
    PipelineRunRepository,
    PipelineRunStatus,
)

logger = logging.getLogger(__name__)
ROOT = Path(__file__).resolve().parents[3]


def initialize(settings):
    """Apply additive, repeatable SQL to new or existing local databases."""
    with connect(settings.database) as connection:
        execute_sql_files(connection, sorted((ROOT / "sql/init").glob("*.sql")))


def download(url: str, target: Path, reuse_cache: bool = False) -> Path:
    target.parent.mkdir(parents=True, exist_ok=True)
    if reuse_cache and target.exists():
        return target
    temporary = target.with_suffix(target.suffix + ".part")
    for attempt in range(3):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "CanadaPulse/0.1"})
            with (
                urllib.request.urlopen(request, timeout=120) as response,
                temporary.open("wb") as output,
            ):
                shutil.copyfileobj(response, output)
            temporary.replace(target)
            return target
        except (urllib.error.URLError, TimeoutError, OSError):
            temporary.unlink(missing_ok=True)
            if attempt == 2:
                raise
            time.sleep(2**attempt)
    raise RuntimeError("Download failed")


def number(value: str, *, nullable: bool = False):
    if not value and nullable:
        return None
    result = Decimal(value)
    if not result.is_finite():
        raise ValueError("Non-finite observation")
    return result


def labour_row(row, run_id, source_table, source_file):
    """Use stable series/date identity so revised values replace earlier observations."""
    reference_date = date.fromisoformat(row["REF_DATE"] + "-01")
    if not row["VECTOR"] or not row["GEO"]:
        raise ValueError("Missing vector or geography")
    identity = f"{source_table}|{row['REF_DATE']}|{row['VECTOR']}|{row['COORDINATE']}"
    return (
        reference_date,
        row["REF_DATE"],
        row["GEO"],
        row["DGUID"],
        row["Labour force characteristics"],
        row.get("Gender", row.get("Sex")),
        row["Age group"],
        row["Statistics"],
        number(row["VALUE"], nullable=True),
        row["UOM"],
        row["SCALAR_FACTOR"],
        row["VECTOR"],
        row["COORDINATE"],
        row["STATUS"],
        row["SYMBOL"],
        row["TERMINATED"],
        int(row["DECIMALS"]) if row["DECIMALS"] else None,
        source_table,
        "Statistics Canada",
        source_file,
        hashlib.sha256(identity.encode()).hexdigest(),
        Jsonb(row),
        run_id,
        row["Data type"],
    )


LABOUR_COLUMNS = [
    "reference_date",
    "reference_period",
    "geography",
    "dguid",
    "labour_force_characteristic",
    "sex",
    "age_group",
    "statistics",
    "value",
    "unit",
    "scalar_factor",
    "vector",
    "coordinate",
    "status",
    "symbol",
    "terminated",
    "decimals",
    "source_table",
    "source",
    "source_file",
    "source_row_hash",
    "raw_payload",
    "pipeline_run_id",
    "data_type",
]
BOC_COLUMNS = [
    "observation_date",
    "series_code",
    "series_name",
    "value",
    "source",
    "raw_payload",
    "pipeline_run_id",
]


def merge_rows(connection, table, columns, keys, rows):
    """COPY into temporary storage, then merge in the caller's transaction."""
    names = sql.SQL(", ").join(map(sql.Identifier, columns))
    with connection.cursor() as cursor:
        cursor.execute(
            sql.SQL(
                "CREATE TEMP TABLE incoming (LIKE raw.{} INCLUDING DEFAULTS) ON COMMIT DROP"
            ).format(sql.Identifier(table))
        )
        count = 0
        with cursor.copy(sql.SQL("COPY incoming ({}) FROM STDIN").format(names)) as copy:
            for row in rows:
                copy.write_row(row)
                count += 1
        if not count:
            raise ValueError("Source returned no observations within the requested scope")
        updates = sql.SQL(", ").join(
            sql.SQL("{} = EXCLUDED.{}").format(sql.Identifier(c), sql.Identifier(c))
            for c in columns
            if c not in keys
        )
        cursor.execute(
            sql.SQL(
                "INSERT INTO raw.{} ({}) SELECT {} FROM incoming "
                "ON CONFLICT ({}) DO UPDATE SET {}, loaded_at = now()"
            ).format(
                sql.Identifier(table),
                names,
                names,
                sql.SQL(", ").join(map(sql.Identifier, keys)),
                updates,
            )
        )
    return count


def run_source(settings, source: str, start: date, reuse_cache: bool = False):
    with connect(settings.database) as meta, connect(settings.database) as data:
        repository = PipelineRunRepository(meta)
        run_id = repository.start_run(f"ingest_{source}", source)
        extracted = 0
        rejected = 0
        try:
            # A session lock avoids overlapping runs for the same source.
            data.execute("SELECT pg_advisory_lock(hashtext(%s))", (f"canadapulse:{source}",))
            cache = ROOT / "data/cache"
            if source == "boc":
                config = yaml.safe_load((ROOT / "config/series.yml").read_text())["bank_of_canada"]
                series = [item for item in config["series"] if item["enabled"]]
                if len(series) != 1:
                    raise ValueError("This pipeline currently requires one configured BoC series")
                item = series[0]
                path = download(
                    f"{config['base_url']}/observations/{item['code']}/json?start_date={start}",
                    cache / f"boc-{item['code']}-{start}.json",
                    reuse_cache,
                )
                payload = json.loads(path.read_text(encoding="utf-8-sig"))

                def rows():
                    nonlocal extracted, rejected
                    for observation in payload["observations"]:
                        extracted += 1
                        try:
                            day = date.fromisoformat(observation["d"])
                            value = number(observation[item["code"]]["v"])
                        except (KeyError, ValueError, ArithmeticError):
                            rejected += 1
                            raise ValueError("Invalid Bank of Canada observation") from None
                        if day >= start:
                            yield (
                                day,
                                item["code"],
                                item["name"],
                                value,
                                "Bank of Canada",
                                Jsonb(observation),
                                run_id,
                            )

                loaded = merge_rows(
                    data,
                    "bank_of_canada_observations",
                    BOC_COLUMNS,
                    ["observation_date", "series_code"],
                    rows(),
                )
            elif source == "statcan":
                config = yaml.safe_load((ROOT / "config/datasets.yml").read_text())["statcan"][
                    "labour_force"
                ]
                if not config["enabled"]:
                    raise ValueError("Statistics Canada source is disabled")
                path = download(config["source_url"], cache / "statcan.zip", reuse_cache)

                def rows():
                    nonlocal extracted, rejected
                    with zipfile.ZipFile(path) as archive:
                        filename = f"{config['pid']}.csv"
                        with archive.open(filename) as stream:
                            reader = csv.DictReader(io.TextIOWrapper(stream, encoding="utf-8-sig"))
                            required = {
                                "REF_DATE",
                                "VECTOR",
                                "COORDINATE",
                                "VALUE",
                                "GEO",
                                "Statistics",
                                "Data type",
                                "Labour force characteristics",
                            }
                            if not required.issubset(reader.fieldnames or []):
                                raise ValueError("Statistics Canada CSV schema changed")
                            for row in reader:
                                # Keep monthly levels, not source-computed changes or errors.
                                if row["REF_DATE"] + "-01" < start.isoformat():
                                    continue
                                if row["Statistics"] != "Estimate":
                                    continue
                                extracted += 1
                                try:
                                    yield labour_row(row, run_id, config["pid"], filename)
                                except (KeyError, ValueError, ArithmeticError):
                                    rejected += 1
                                    raise ValueError(
                                        f"Invalid Statistics Canada row {reader.line_num}"
                                    ) from None

                loaded = merge_rows(
                    data, "statcan_labour_force", LABOUR_COLUMNS, ["source_row_hash"], rows()
                )
            else:
                raise ValueError(f"Unknown source: {source}")
            # Finalize metadata in the same transaction as the observations.
            PipelineRunRepository(data).complete_run(
                run_id,
                counts=PipelineRunCounts(extracted, loaded, rejected),
            )
            logger.info(
                "Ingestion complete", extra={"pipeline_run_id": str(run_id), "source_name": source}
            )
            return {"source": source, "run_id": str(run_id), "rows_loaded": loaded}
        except Exception as exc:
            data.rollback()
            repository.complete_run(
                run_id,
                status=PipelineRunStatus.FAILED,
                counts=PipelineRunCounts(extracted, 0, rejected),
                error_message=str(exc),
            )
            raise
