from datetime import UTC, datetime

from fastapi import FastAPI
from fastapi.testclient import TestClient

from canadapulse.api.v1 import create_router


def test_history_parameterization_and_public_contract():
    calls = []

    def query(statement, parameters=()):
        calls.append((statement, parameters))
        return [
            {
                "date": "2025-01-01",
                "geography": "Canada",
                "indicator": "Employment",
                "gender": "Total - Gender",
                "age_group": "15 years and over",
                "adjustment": "Seasonally adjusted",
                "value": None,
                "unit": "Persons in thousands",
                "scalar_factor": "thousands",
                "loaded_at": datetime.now(UTC),
                "raw_payload": {"private": "must not leak"},
            }
        ]

    app = FastAPI()
    app.include_router(create_router(query))
    with TestClient(app) as client:
        response = client.get("/api/v1/labour/history", params={"geography": "Canada' OR 1=1--"})
        assert response.status_code == 200
        assert response.json()[0]["value"] is None
        assert "raw_payload" not in response.json()[0]
        assert "Canada' OR 1=1--" not in calls[0][0]
        assert calls[0][1][0] == "Canada' OR 1=1--"
        assert client.get("/api/v1/labour/history?limit=5001").status_code == 422
        assert (
            client.get(
                "/api/v1/labour/history?start_date=2025-02-01&end_date=2025-01-01"
            ).status_code
            == 422
        )


def test_empty_pipeline_is_not_healthy():
    app = FastAPI()
    app.include_router(create_router(lambda *args: []))
    with TestClient(app) as client:
        data = client.get("/api/v1/pipeline/status").json()
        assert data["status"] == "degraded"
        assert data["last_successful_refresh"] is None
        assert data["quality_checks"] == 0
