"""Read-only dashboard API with explicit dimensions and bounded result sets."""

from datetime import date
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from psycopg import Error as PsycopgError
from psycopg.rows import dict_row

from canadapulse.api.v1 import create_router
from canadapulse.config import load_settings
from canadapulse.database.connection import connect
from canadapulse.exceptions import DatabaseConnectionError

app = FastAPI(
    title="CanadaPulse",
    version="0.2.0",
    description=(
        "Canadian Economic & Labour Market Intelligence. Versioned endpoints serve dbt marts; "
        "Legacy routes preserve the local explorer. Independent portfolio project; "
        "not a government service."
    ),
)


def query(statement, parameters=()):
    try:
        with connect(load_settings().database) as connection:
            connection.execute("SET TRANSACTION READ ONLY")
            connection.execute("SET LOCAL statement_timeout = '15s'")
            with connection.cursor(row_factory=dict_row) as cursor:
                cursor.execute(statement, parameters)
                return cursor.fetchall()
    except (DatabaseConnectionError, PsycopgError):
        raise HTTPException(
            503, "Data is temporarily unavailable. Please try again later."
        ) from None


app.include_router(create_router(query))
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(load_settings().cors_origins),
    allow_methods=["GET"],
    allow_headers=["Accept", "Content-Type"],
)


@app.get("/", response_class=HTMLResponse)
def dashboard():
    return Path(__file__).with_name("dashboard.html").read_text(encoding="utf-8")


@app.get("/api/health")
def health():
    try:
        query("SELECT 1 AS ok")
    except Exception:
        raise HTTPException(503, "Database unavailable") from None
    return {"status": "ok"}


@app.get("/api/filters")
def filters():
    # Identifiers are a fixed allowlist, never interpolated from user input.
    result = {}
    for column in ("geography", "indicator", "gender", "age_group", "adjustment"):
        result[column] = [
            row["value"]
            for row in query(
                f"SELECT DISTINCT {column} AS value FROM analytics.labour_market "
                f"WHERE {column} IS NOT NULL ORDER BY {column}"
            )
        ]
    result["coverage"] = query(
        "SELECT min(date) AS start_date, max(date) AS end_date, count(*) AS rows "
        "FROM analytics.labour_market"
    )[0]
    return result


@app.get("/api/labour")
def labour(
    geography: str = "Canada",
    indicator: str = "Unemployment rate",
    gender: str = "Total - Gender",
    age_group: str = "15 years and over",
    adjustment: str = "Seasonally adjusted",
    start_date: date = date(2015, 1, 1),
    end_date: date = date(2100, 1, 1),
    limit: int = Query(1000, ge=1, le=5000),
    offset: int = Query(0, ge=0),
):
    if start_date > end_date:
        raise HTTPException(422, "start_date must be on or before end_date")
    return query(
        "SELECT * FROM analytics.labour_market WHERE geography = %s AND indicator = %s "
        "AND gender = %s AND age_group = %s AND adjustment = %s "
        "AND date BETWEEN %s AND %s ORDER BY date, vector LIMIT %s OFFSET %s",
        (geography, indicator, gender, age_group, adjustment, start_date, end_date, limit, offset),
    )


@app.get("/api/rates")
def rates(
    start_date: date = date(2015, 1, 1),
    end_date: date = date(2100, 1, 1),
    limit: int = Query(5000, ge=1, le=20000),
    offset: int = Query(0, ge=0),
):
    if start_date > end_date:
        raise HTTPException(422, "start_date must be on or before end_date")
    return query(
        "SELECT * FROM analytics.interest_rates WHERE date BETWEEN %s AND %s "
        "ORDER BY date, series_code LIMIT %s OFFSET %s",
        (start_date, end_date, limit, offset),
    )


@app.get("/api/runs")
def runs():
    return query(
        "SELECT pipeline_run_id, source_name, started_at, completed_at, status, "
        "records_extracted, records_loaded, records_rejected, duration_seconds "
        "FROM metadata.pipeline_runs ORDER BY started_at DESC LIMIT 20"
    )


@app.get("/api/comparison")
def comparison(
    observation_date: date,
    indicator: str = "Unemployment rate",
    gender: str = "Total - Gender",
    age_group: str = "15 years and over",
    adjustment: str = "Seasonally adjusted",
):
    """Compare like-for-like observations at exactly the same monthly reference date."""
    return query(
        "SELECT geography, value, unit, date FROM analytics.labour_market "
        "WHERE date = %s AND indicator = %s AND gender = %s "
        "AND age_group = %s AND adjustment = %s ORDER BY value DESC NULLS LAST, geography",
        (observation_date, indicator, gender, age_group, adjustment),
    )
