# Orchestration

The reusable execution path is `python -m canadapulse.cli refresh`. Python owns source
clients, validation, upserts and metadata; dbt owns warehouse transformations and assertions.
Schedulers call these functions without copying business rules.

## GitHub Actions deployment schedule

`refresh-data.yml` runs at 21:30 UTC on weekdays when repository variable
ENABLE_PRODUCTION_REFRESH is true and the production environment has a writer DATABASE_URL.
The Bank of Canada refreshes each weekday. The Statistics Canada archive refreshes Fridays,
capturing monthly releases and subsequent revisions without fetching a 60 MB archive daily.
Manual dispatch supports all, boc, or statcan. A dbt build follows the selected imports.
GitHub schedule timing is best effort, not a source-release SLA. Source freshness tolerances
allow the weekly labour schedule and weekends for interest rates.

The workflow uses read-only repository permissions, no production credentials in pull requests,
one production concurrency group, a 45-minute timeout, and no cache reuse for published data.
If an import/build fails, the job fails; source/warehouse metadata retains the failure. Configure
owner notifications in GitHub. Repository inactivity can disable scheduled workflows; check
GitHub settings and the public pipeline page rather than assuming a scheduler is running.

## Optional Airflow

The Airflow 3 DAG has initialization, independent source tasks, and a dependent dbt build/test
task. Source tasks have two retries with a five-minute delay. Timeouts, no historical catchup,
and one active DAG run keep repeated work bounded. `dbt build` executes models and tests in
dependency order; separating run/test into duplicate task logic would lose that useful ordering.
Quality outcomes are recorded by the same warehouse service used by GitHub Actions.

```bash
docker compose -f docker-compose.yml -f docker-compose.airflow.yml --profile airflow up --build
```

This starts an authenticated, localhost-only standalone Airflow demonstration. Retrieve its
generated admin login from local container output. DAGs start paused. Unpause only when ready
to download official data. The demo metadata is ephemeral; a managed Airflow deployment needs
its own persistent metadata database and secrets backend. Never publish this standalone UI.

Airflow runs on Linux containers, not native Windows. Application code is installed in its
image; parsing the DAG makes no HTTP or warehouse calls. Use the same worker image and
environment settings for all tasks. Its weekly DAG demonstrates independent task retries and
dependencies. During inexpensive hosting, GitHub Actions is the primary scheduler; do not
enable both schedulers for the same production database.
