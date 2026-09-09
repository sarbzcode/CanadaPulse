"""Versioned public API reading curated dbt serving marts."""

from collections.abc import Callable
from datetime import UTC, date, datetime, timedelta
from typing import Annotated, Any

from fastapi import APIRouter, HTTPException, Query

from canadapulse.api.schemas import (
    Geography,
    Headline,
    Health,
    Indicator,
    InterestObservation,
    LabourObservation,
    PipelineRun,
    PipelineStatus,
    Summary,
)
from canadapulse.config import load_settings

Label = Annotated[str, Query(min_length=1, max_length=150)]


def create_router(query: Callable[..., list[dict[str, Any]]]) -> APIRouter:
    router = APIRouter()

    @router.get("/api/v1/filters", response_model=dict[str, list[str]], tags=["Labour"])
    def filters():
        """Available demographic labels from the curated serving model."""
        return {
            column: [
                row["value"]
                for row in query(
                    f"SELECT DISTINCT {column} AS value FROM analytics.labour_observations "
                    f"WHERE {column} IS NOT NULL ORDER BY {column}"
                )
            ]
            for column in ("geography", "indicator", "gender", "age_group", "adjustment")
        }

    @router.get("/health", response_model=Health, tags=["System"])
    def health():
        """Safe readiness status: database connectivity plus freshness of the serving warehouse."""
        query("SELECT 1")
        state = pipeline_status()
        return {
            "status": state["status"],
            "database": "healthy",
            "version": load_settings().service_version,
            "last_pipeline_run": state["last_run"],
            "last_successful_refresh": state["last_successful_refresh"],
        }

    @router.get("/api/v1/provinces", response_model=list[Geography], tags=["Labour"])
    def provinces():
        """Observed geographies, including Canada. No fabricated territorial observations."""
        return query(
            "SELECT geography_name, geography_type, province_code, region "
            "FROM warehouse.dim_geography ORDER BY geography_name"
        )

    @router.get("/api/v1/indicators", response_model=list[Indicator], tags=["Labour"])
    def indicators():
        return query(
            "SELECT indicator_name, unit, indicator_category, description "
            "FROM warehouse.dim_indicator ORDER BY indicator_name"
        )

    @router.get("/api/v1/labour/history", response_model=list[LabourObservation], tags=["Labour"])
    def history(
        geography: Label = "Canada",
        indicator: Label = "Unemployment rate",
        gender: Label = "Total - Gender",
        age_group: Label = "15 years and over",
        adjustment: Label = "Seasonally adjusted",
        start_date: date | None = None,
        end_date: date | None = None,
        limit: int = Query(600, ge=1, le=5000),
        offset: int = Query(0, ge=0, le=100000),
    ):
        """One demographic series in original units. Default window: 5 years."""
        start = start_date or date.today() - timedelta(days=5 * 366)
        end = end_date or date.today()
        if start > end:
            raise HTTPException(422, "start_date must be on or before end_date")
        return query(
            "SELECT date, geography, indicator, gender, age_group, adjustment, value, unit, "
            "scalar_factor, source_status, loaded_at FROM analytics.labour_observations "
            "WHERE geography=%s AND indicator=%s AND gender=%s AND age_group=%s "
            "AND adjustment=%s AND date BETWEEN %s AND %s ORDER BY date, observation_key "
            "LIMIT %s OFFSET %s",
            (geography, indicator, gender, age_group, adjustment, start, end, limit, offset),
        )

    @router.get("/api/v1/labour/latest", response_model=Headline | None, tags=["Labour"])
    def latest(geography: Label = "Canada"):
        """Headline scope: total gender, ages 15+, seasonally adjusted. Counts are persons."""
        rows = query(
            "SELECT * FROM analytics.province_labour_summary WHERE geography=%s "
            "ORDER BY reference_date DESC LIMIT 1",
            (geography,),
        )
        return rows[0] if rows else None

    @router.get("/api/v1/labour/compare", response_model=list[Headline], tags=["Labour"])
    def compare(observation_date: date | None = None):
        """All observed provinces at one reference month; never mix each province's latest month."""
        return query(
            "SELECT * FROM analytics.province_comparison WHERE reference_date = "
            "coalesce(%s, (SELECT max(reference_date) FROM analytics.province_comparison)) "
            "ORDER BY unemployment_rate DESC NULLS LAST, geography",
            (observation_date,),
        )

    @router.get(
        "/api/v1/economy/interest-rates", response_model=list[InterestObservation], tags=["Economy"]
    )
    def interest_rates(
        start_date: date | None = None,
        end_date: date | None = None,
        series_code: Label = "V39079",
        limit: int = Query(2000, ge=1, le=20000),
        offset: int = Query(0, ge=0, le=100000),
    ):
        start, end = start_date or date.today() - timedelta(days=5 * 366), end_date or date.today()
        if start > end:
            raise HTTPException(422, "start_date must be on or before end_date")
        return query(
            "SELECT date, series_code, series_name, rate, loaded_at "
            "FROM analytics.interest_rate_history WHERE series_code=%s "
            "AND date BETWEEN %s AND %s ORDER BY date LIMIT %s OFFSET %s",
            (series_code, start, end, limit, offset),
        )

    @router.get("/api/v1/dashboard/summary", response_model=Summary, tags=["Labour"])
    def summary():
        rate = query(
            "SELECT date, series_code, series_name, rate, loaded_at "
            "FROM analytics.interest_rate_history WHERE series_code='V39079' "
            "ORDER BY date DESC LIMIT 1"
        )
        refresh = query(
            "SELECT max(completed_at) as refreshed FROM metadata.pipeline_runs "
            "WHERE source_name='warehouse' AND status='SUCCESS'"
        )[0]["refreshed"]
        return {
            "labour": latest(),
            "interest_rate": rate[0] if rate else None,
            "warehouse_refreshed_at": refresh,
        }

    @router.get("/api/v1/pipeline/runs", response_model=list[PipelineRun], tags=["Pipeline"])
    def runs(limit: int = Query(20, ge=1, le=100)):
        return query(
            "SELECT pipeline_run_id, source_name, started_at, completed_at, status, "
            "records_extracted, records_loaded, records_rejected, duration_seconds, "
            "records_inserted, records_updated, records_unchanged, latest_reference_date "
            "FROM metadata.pipeline_runs ORDER BY started_at DESC LIMIT %s",
            (limit,),
        )

    @router.get("/api/v1/pipeline/status", response_model=PipelineStatus, tags=["Pipeline"])
    def pipeline_status():
        """Actual latest runs and measured checks; missing or stale sources are not healthy."""
        sources = []
        latest_ids = []
        last_run = None
        warehouse_refresh = None
        now = datetime.now(UTC)
        for source, max_days in [("boc", 4), ("statcan", 8), ("warehouse", 4)]:
            recent = query(
                "SELECT pipeline_run_id, status, started_at FROM metadata.pipeline_runs "
                "WHERE source_name=%s ORDER BY started_at DESC LIMIT 1",
                (source,),
            )
            good = query(
                "SELECT pipeline_run_id, completed_at, records_loaded, duration_seconds, "
                "latest_reference_date FROM metadata.pipeline_runs "
                "WHERE source_name=%s AND status='SUCCESS' "
                "ORDER BY completed_at DESC LIMIT 1",
                (source,),
            )
            record = {"source": source, "status": "not_loaded"}
            if recent:
                latest_ids.append(recent[0]["pipeline_run_id"])
                record["last_run"] = recent[0]["started_at"]
                last_run = max(last_run or record["last_run"], record["last_run"])
                record["status"] = {
                    "FAILED": "failed",
                    "PARTIAL": "degraded",
                    "RUNNING": "running",
                    "SUCCESS": "healthy",
                }[recent[0]["status"]]
            if good:
                g = good[0]
                record.update(
                    last_successful_run=g["completed_at"],
                    records_processed=g["records_loaded"],
                    duration_seconds=g["duration_seconds"],
                    latest_reference_date=g["latest_reference_date"],
                )
                if record["status"] == "healthy" and now - g["completed_at"] > timedelta(
                    days=max_days
                ):
                    record["status"] = "stale"
                if source == "warehouse":
                    warehouse_refresh = g["completed_at"]
            sources.append(record)
        quality = query(
            "SELECT check_name, table_name, status, observed_value, "
            "expected_condition, checked_at FROM metadata.data_quality_results "
            "WHERE pipeline_run_id = ANY(%s) ORDER BY checked_at DESC",
            (latest_ids,),
        )
        failed = sum(q["status"] == "FAIL" for q in quality)
        return {
            "status": "healthy"
            if all(s["status"] == "healthy" for s in sources) and not failed
            else "degraded",
            "last_run": last_run,
            "last_successful_refresh": warehouse_refresh,
            "sources": sources,
            "quality_checks": len(quality),
            "quality_failures": failed,
            "quality_results": quality,
        }

    return router
