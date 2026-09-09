"""Opt-in real PostgreSQL tests, isolated in a disposable database."""

import csv
import io
import json
import os
import zipfile
from dataclasses import replace
from datetime import date
from uuid import uuid4

import psycopg
import pytest
from fastapi.testclient import TestClient
from psycopg import sql

from canadapulse.api import app as api
from canadapulse.config import load_settings
from canadapulse.database.connection import connect
from canadapulse.ingestion import pipelines

pytestmark = pytest.mark.skipif(
    os.getenv("CANADAPULSE_INTEGRATION") != "1", reason="Set CANADAPULSE_INTEGRATION=1"
)


@pytest.fixture
def settings():
    base = load_settings()
    name = "canadapulse_test_" + uuid4().hex
    with psycopg.connect(**base.database.as_connection_kwargs(), autocommit=True) as admin:
        admin.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(name)))
        try:
            isolated = replace(base, database=replace(base.database, database=name))
            pipelines.initialize(isolated)
            yield isolated
        finally:
            admin.execute(sql.SQL("DROP DATABASE {} WITH (FORCE)").format(sql.Identifier(name)))


def test_atomic_revisions_validation_and_dashboard(settings, tmp_path, monkeypatch):
    path = tmp_path / "boc.json"
    monkeypatch.setattr(pipelines, "download", lambda *args: path)

    def write(values):
        path.write_text(json.dumps({"observations": values}), encoding="utf-8")

    def rates():
        with connect(settings.database) as connection:
            return connection.execute(
                "SELECT value FROM raw.bank_of_canada_observations ORDER BY observation_date"
            ).fetchall()

    write([{"d": "2025-01-01", "V39079": {"v": "3.00"}}])
    pipelines.run_source(settings, "boc", date(2025, 1, 1))
    pipelines.run_source(settings, "boc", date(2025, 1, 1))
    assert len(rates()) == 1
    write([{"d": "2025-01-01", "V39079": {"v": "3.25"}}])
    pipelines.run_source(settings, "boc", date(2025, 1, 1))
    assert float(rates()[0][0]) == 3.25
    write(
        [{"d": "2025-01-01", "V39079": {"v": "4.00"}}, {"d": "2025-01-02", "V39079": {"v": "NaN"}}]
    )
    with pytest.raises(ValueError, match="Invalid Bank"):
        pipelines.run_source(settings, "boc", date(2025, 1, 1))
    assert float(rates()[0][0]) == 3.25
    with connect(settings.database) as connection:
        assert connection.execute(
            "SELECT records_loaded, records_rejected FROM metadata.pipeline_runs "
            "WHERE status = 'FAILED'"
        ).fetchone() == (0, 1)

    row = {
        "REF_DATE": "2025-01",
        "GEO": "Canada",
        "DGUID": "country",
        "Labour force characteristics": "Unemployment rate",
        "Gender": "Total - Gender",
        "Age group": "15 years and over",
        "Statistics": "Estimate",
        "Data type": "Seasonally adjusted",
        "VALUE": "6.5",
        "UOM": "Percent",
        "SCALAR_FACTOR": "units",
        "VECTOR": "v123",
        "COORDINATE": "1.1.1",
        "STATUS": "",
        "SYMBOL": "",
        "TERMINATED": "",
        "DECIMALS": "1",
    }
    path = tmp_path / "statcan.zip"

    def write_labour():
        stream = io.StringIO()
        writer = csv.DictWriter(stream, fieldnames=list(row))
        writer.writeheader()
        writer.writerow(row)
        writer.writerow({**row, "REF_DATE": "2010-01"})
        writer.writerow({**row, "Statistics": "Standard error", "VECTOR": "v999"})
        with zipfile.ZipFile(path, "w") as archive:
            archive.writestr("14100287.csv", stream.getvalue())

    write_labour()
    pipelines.run_source(settings, "statcan", date(2025, 1, 1))
    row["VALUE"] = "6.7"
    write_labour()
    pipelines.run_source(settings, "statcan", date(2025, 1, 1))
    monkeypatch.setattr(api, "load_settings", lambda: settings)
    with TestClient(api.app) as client:
        assert client.get("/api/health").status_code == 200
        assert client.get("/").status_code == 200
        labour = client.get("/api/labour").json()
        assert len(labour) == 1
        assert float(labour[0]["value"]) == 6.7
        assert client.get("/api/filters").json()["coverage"]["rows"] == 1
        assert client.get("/api/labour?geography=Canada%27%20OR%201=1--").json() == []
        assert client.get("/api/labour?limit=5001").status_code == 422
        assert client.get("/api/rates?start_date=2026-01-01&end_date=2025-01-01").status_code == 422
        assert len(client.get("/api/rates").json()) == 1
        comparison = client.get("/api/comparison?observation_date=2025-01-01").json()
        assert len(comparison) == 1
        assert comparison[0]["geography"] == "Canada"
        assert float(comparison[0]["value"]) == 6.7
        assert client.get("/api/comparison?observation_date=2025-02-01").json() == []
        assert client.get(
            "/api/comparison?observation_date=2025-01-01&gender=Women%2B"
        ).json() == []
        assert client.get("/api/comparison").status_code == 422
    row["VALUE"] = ""
    row["STATUS"] = "x"
    write_labour()
    pipelines.run_source(settings, "statcan", date(2025, 1, 1))
    with connect(settings.database) as connection:
        assert connection.execute("SELECT value FROM analytics.labour_market").fetchone() == (None,)
