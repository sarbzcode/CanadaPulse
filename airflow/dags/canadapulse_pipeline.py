"""Optional weekly orchestration; business logic lives in the application package."""

from datetime import UTC, datetime, timedelta

from airflow.sdk import dag, task


@dag(
    dag_id="canadapulse_pipeline",
    schedule="30 21 * * 5",
    start_date=datetime(2025, 1, 1, tzinfo=UTC),
    catchup=False,
    max_active_runs=1,
    default_args={"retries": 2, "retry_delay": timedelta(minutes=5)},
    tags=["canadapulse", "batch", "warehouse"],
    description="Independent source imports followed by a tested, tracked dbt warehouse build.",
)
def canadapulse_pipeline():
    @task(execution_timeout=timedelta(minutes=5))
    def initialize_database():
        from canadapulse.config import load_settings
        from canadapulse.ingestion.pipelines import initialize

        initialize(load_settings())

    @task(execution_timeout=timedelta(minutes=30))
    def ingest(source: str):
        from datetime import date

        from canadapulse.config import load_settings
        from canadapulse.ingestion.pipelines import run_source
        from canadapulse.logging_config import configure_logging

        settings = load_settings()
        configure_logging(settings.log_level)
        return run_source(settings, source, date(2015, 1, 1))

    @task(execution_timeout=timedelta(minutes=20))
    def build_and_test_warehouse():
        from canadapulse.services.warehouse_service import refresh_warehouse

        # dbt build couples dependency ordering and assertions; failures are persisted and raised.
        return refresh_warehouse()

    initialized = initialize_database()
    labour = ingest.override(task_id="ingest_statcan")("statcan")
    rates = ingest.override(task_id="ingest_bank_of_canada")("boc")
    initialized >> [labour, rates] >> build_and_test_warehouse()


canadapulse_pipeline()
