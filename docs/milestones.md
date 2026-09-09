# Implementation verification ledger

## Milestone 1 — inspected baseline

- Completed: inspected application, SQL, tests, source configuration, documentation and empty extension directories.
- Architecture changes: none; preserved working source ingestion and local explorer.
- Files added: this ledger.
- Files modified: none for stabilization.
- Tests run: 17 pytest tests passed, including isolated PostgreSQL integration; Ruff passed.
- Current state: raw data, analytics views, API and browser dashboard work.
- How to run: README local commands.
- Next milestone: dbt foundation, star schema and analytics marts.

## Milestones 2–4 — warehouse and curated API

- Completed: dbt sources, staging, intermediate models, star schema, analytics marts, typed versioned API; preserved legacy routes and dashboard.
- Architecture changes: raw -> dbt -> indexed analytics -> versioned FastAPI; deterministic keys and explicit demographic/unit grain.
- Files added: `warehouse/`, `services/warehouse_service.py`, `api/v1.py`, `api/schemas.py`, warehouse/model guides and fixture scripts.
- Files modified: dependency configuration, CLI and API integration.
- Tests run: dbt deps/debug/run/test/docs generation succeeded; final real-data build reported `PASS=84 WARN=0 ERROR=0 SKIP=0` (16 models, 1 seed, 67 tests). Disposable fixture database build and semantic API assertions passed.
- Current state: curated models serve actual observations; source identity and lineage are preserved.
- How to run: `python -m canadapulse.cli warehouse`; see `docs/warehouse.md`.
- Next milestone: measured quality and safe public status.

## Milestones 5–7 — observability, CI and deployment configuration

- Completed: real insert/update/unchanged counts, source/dbt quality results, safe status API, Python/dbt CI, hosted PostgreSQL URL/SSL, CORS, API container and Render configuration.
- Architecture changes: additive metadata migration; reader queries run in read-only transactions with bounded execution time.
- Files added: `005_observability.sql`, `validation/quality.py`, workflow definitions, Dockerfile, Render blueprint, deployment guide and API server entry point.
- Files modified: ingestion load metrics, logging, database/configuration modules, environment example and Docker Compose.
- Tests run: 26 pytest tests passed, including isolated PostgreSQL integration; Ruff passed. Two upstream deprecation warnings remain. Built the API image and verified HTTP 200 responses for health, summary and pipeline status against the actual local database.
- Current state: READY FOR DEPLOYMENT; external accounts, database and public domains still require provisioning.
- How to run: `python -m canadapulse.cli refresh`; follow `docs/deployment.md` for hosting.
- Next milestone: public frontend.

## Milestones 8–9 — public website

- Completed: overview, provinces, trends, economy, explorer, pipeline and about pages; actual API data, chart/filter controls, CSV, loading/error/empty states, source attribution and responsive layout.
- Architecture changes: Next.js/TypeScript frontend alongside the retained original dashboard; bounded API requests and five-minute homepage revalidation.
- Files added: `frontend/`, frontend CI and real browser screenshots.
- Files modified: README and environment/deployment documentation.
- Tests run: npm lint, TypeScript checking and production build passed. Browser verification covered all seven pages, province selection and mobile layout with no JavaScript exceptions or horizontal page overflow. Final npm ci reported zero vulnerabilities; lint, typecheck and production build passed again. Browser CSV export, empty results, invalid date range and blocked-API error states also passed.
- Current state: local application works; Vercel configuration uses an environment-supplied API URL.
- How to run: `cd frontend`, `npm ci`, `npm run dev`.
- Next milestone: scheduling and optional orchestration.

## Milestones 10–11 — scheduling and Airflow

- Completed: opt-in production GitHub Actions workflow; weekday rates and Friday labour imports; alternative authenticated local Airflow orchestration with retries and independent source tasks.
- Architecture changes: scheduling calls existing Python/dbt business logic. Enable one production scheduler, not both.
- Files added: scheduled workflow, `scripts/refresh_scheduled.py`, Airflow DAG/image/Compose and orchestration guide.
- Files modified: scheduler unit coverage and README.
- Tests run: source-selection unit tests passed. Built the Airflow 3.3.1 image; imported its four-task DAG and asserted both ingestion tasks precede the warehouse task. A complete Airflow-scheduled production run has not been claimed.
- Current state: local DAG is importable; production workflow remains guarded until credentials and opt-in variable exist.
- How to run: `docs/orchestration.md`.
- Next milestone: BI and optional Spark/cloud component.

## Milestones 12–14 — portfolio and optional analytical components

- Completed: Power BI model/measure guide, runnable Spark transformation, optional Azure/Databricks architecture, decision records, architecture/data-model diagrams, deployment guide and employer-facing README.
- Architecture changes: optional Spark export/Parquet demonstration is separate from the core PostgreSQL/dbt runtime; local development needs no paid cloud resources.
- Files added: `spark/jobs/`, `scripts/export_spark_input.py`, BI/Spark guides, decision records and screenshots.
- Files modified: README, architecture, cloud architecture, data model and pipeline documentation.
- Tests run: official Spark 4.0.1 container successfully wrote partitioned Parquet from actual exported data: 13,860 monthly observations and 1,188 annual groups in that execution. These are measured local verification results, not permanent product-scale claims.
- Current state: repository implementation ready; live public hosting and a real Power BI report remain external/optional deliverables. No fake URLs or PBIX files are included.
- How to run: `docs/spark.md`, `docs/power-bi.md`, `docs/deployment.md`.
- Next milestone: provision hosting, configure secrets/CORS, verify real public URLs, then observe scheduled refreshes.

## GitHub verification follow-up

The first uploaded commit passed dbt and frontend CI. Python CI exposed an existing dotenv
test's dependence on ambient database variables. Configuration tests now clear inherited
application variables within a scoped pytest fixture; production configuration precedence is
unchanged. Reproduced locally with process-level database settings: 26 tests passed and Ruff
passed. Follow the README workflow badges for the latest remote result.
