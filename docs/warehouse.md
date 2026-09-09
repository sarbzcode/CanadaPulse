# Warehouse development

Install the optional warehouse dependencies in an isolated Python 3.11–3.13 environment:

```powershell
python -m pip install -e '.[dev,warehouse]'
python -m canadapulse.cli init-db
python -m canadapulse.services.warehouse_service deps
python -m canadapulse.services.warehouse_service debug
python -m canadapulse.services.warehouse_service seed
python -m canadapulse.services.warehouse_service run
python -m canadapulse.services.warehouse_service test
python -m canadapulse.services.warehouse_service docs generate
python -m canadapulse.services.warehouse_service docs serve
```

The wrapper uses the same validated database settings as ingestion and keeps passwords out
of command arguments. It exports DBT_ENV_SECRET_PASSWORD so dbt redacts it in logs. The
checked-in profiles.yml contains environment lookups only. Direct `dbt deps`, `dbt debug`,
`dbt run`, `dbt test`, and `dbt docs generate` work from warehouse/ with `--profiles-dir .`
when DBT_HOST, DBT_PORT, DBT_USER, DBT_ENV_SECRET_PASSWORD, DBT_DATABASE and DBT_SSLMODE are set.
Run `dbt seed` once before the first `dbt run`. `dbt build` includes seeds, models and tests.

The project pins Core to the 1.11 release line and the PostgreSQL adapter to 1.10. A daily
calendar uses YYYYMMDD integer keys. Geography, indicator and series keys hash JSON arrays
of their natural keys, avoiding ambiguous concatenation. Hashes are identifiers, not security
controls. Observation keys retain source identity so revisions do not duplicate facts.

Staging and intermediate models are views. Facts, dimensions and serving marts are tables:
a full rebuild captures source revisions and makes serving reads independent of raw-table
joins. At the current measured size this is simpler than incremental change detection.
Refresh models after ingestion; the original local views remain available during migration.

Schema names are staging, intermediate, warehouse and analytics. DBT_SCHEMA_PREFIX can
isolate developer models; use a separate database for CI. Raw sources use DBT_RAW_SCHEMA
(default raw). Never point fixture loading at production. No third-party macro package is
needed: packages.yml is intentionally empty.

Headline scope: Total - Gender, 15 years and over, Seasonally adjusted, Estimate. Employment
and unemployment in headline marts are persons (source thousands multiplied by 1000).
Explorer facts retain source values and units. Monthly changes check the previous calendar
month; year-over-year values join the exact month a year earlier. Missing observations stay
null. Economic alignment chooses the last observed V39079 rate *within* each labour month,
retains its date, and flags unfinished months. No forward fill across missing months and no
causal claim are made.

Source freshness describes last ingestion, not publication month. The source monthly release
period is reported separately by the API. Fact reconciliation and business-grain tests protect
against fan-out, loss and inappropriate dimension aggregation. See data-model.md for grains.
