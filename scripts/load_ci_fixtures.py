"""Small synthetic dataset ONLY for disposable *_ci databases; no government HTTP calls."""

from datetime import date

from psycopg.types.json import Jsonb

from canadapulse.config import load_settings
from canadapulse.database.connection import connect
from canadapulse.database.metadata import PipelineRunCounts, PipelineRunRepository
from canadapulse.ingestion.pipelines import (
    BOC_COLUMNS,
    LABOUR_COLUMNS,
    initialize,
    labour_row,
    merge_rows,
)


def main() -> None:
    settings = load_settings()
    if not settings.database.database.endswith("_ci"):
        raise RuntimeError("Fixtures are restricted to disposable database names ending in _ci")
    initialize(settings)
    with connect(settings.database) as c:
        repository = PipelineRunRepository(c)
        run_id = repository.start_run("fixture_labour", "statcan")
        observations = []
        for index in range(15):
            day = date(2024 + index // 12, index % 12 + 1, 1)
            for geo in ["Canada", "Nova Scotia"]:
                for indicator, value, unit in [
                    ("Employment", str(100 + index), "Persons in thousands"),
                    ("Unemployment", "10", "Persons in thousands"),
                    ("Unemployment rate", "6.5", "Percent"),
                    ("Employment rate", "60.0", "Percent"),
                    ("Participation rate", "65.0", "Percent"),
                ]:
                    row = {
                        "REF_DATE": day.strftime("%Y-%m"),
                        "GEO": geo,
                        "DGUID": "fixture",
                        "Labour force characteristics": indicator,
                        "Gender": "Total - Gender",
                        "Age group": "15 years and over",
                        "Statistics": "Estimate",
                        "Data type": "Seasonally adjusted",
                        "VALUE": value,
                        "UOM": unit,
                        "SCALAR_FACTOR": "units" if unit == "Percent" else "thousands",
                        "VECTOR": geo + indicator,
                        "COORDINATE": geo + indicator,
                        "STATUS": "",
                        "SYMBOL": "",
                        "TERMINATED": "",
                        "DECIMALS": "1",
                    }
                    observations.append(labour_row(row, run_id, "14100287", "ci_fixture.csv"))
        measured = merge_rows(
            c, "statcan_labour_force", LABOUR_COLUMNS, ["source_row_hash"], observations
        )
        repository.complete_run(run_id, counts=PipelineRunCounts(measured.loaded, measured.loaded))
        run_id = repository.start_run("fixture_rates", "boc")
        rates = [
            (
                date(2024 + i // 12, i % 12 + 1, 15),
                "V39079",
                "target_overnight_rate",
                3.25,
                "Bank of Canada",
                Jsonb({"fixture": True}),
                run_id,
            )
            for i in range(15)
        ]
        measured = merge_rows(
            c,
            "bank_of_canada_observations",
            BOC_COLUMNS,
            ["observation_date", "series_code"],
            rates,
        )
        repository.complete_run(run_id, counts=PipelineRunCounts(measured.loaded, measured.loaded))


if __name__ == "__main__":
    main()
