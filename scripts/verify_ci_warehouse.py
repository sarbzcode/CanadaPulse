"""Check actual mart semantics and API contracts after dbt builds the CI fixtures."""

from fastapi.testclient import TestClient

from canadapulse.api.app import app
from canadapulse.config import load_settings
from canadapulse.database.connection import connect


def main() -> None:
    settings = load_settings()
    if not settings.database.database.endswith("_ci"):
        raise RuntimeError("Only run fixture assertions against a *_ci database")
    with connect(settings.database) as c:
        record = c.execute(
            "SELECT employment, monthly_employment_change, yoy_employment_change, "
            "overnight_rate, rate_observation_date FROM analytics.economic_dashboard "
            "WHERE reference_date='2025-01-01'"
        ).fetchone()
        assert record[:4] == (112000, 1000, 12000, 3.25), record
        assert str(record[4]) == "2025-01-15"
    with TestClient(app) as client:
        assert client.get("/api/v1/labour/latest").json()["employment"] == 114000
        assert len(client.get("/api/v1/labour/compare").json()) == 1
        assert client.get("/api/v1/dashboard/summary").status_code == 200
        assert client.get("/docs").status_code == 200
    print("Warehouse semantics and public API fixture checks passed.")


if __name__ == "__main__":
    main()
