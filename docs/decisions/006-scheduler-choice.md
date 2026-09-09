# GitHub Actions and Airflow are alternatives

## Context

The portfolio needs observable automation without making public hosting depend on an always-on orchestration server.

## Decision

Use guarded GitHub Actions scheduling during initial hosting. Include an optional authenticated local Airflow DAG that calls the same application functions. Enable only one production scheduler.

## Alternatives

Always-on Airflow for every deployment, cron with untracked scripts, or business logic embedded in DAGs.

## Consequences

GitHub is inexpensive but schedule timing is best effort. Airflow demonstrates per-task retries and dependencies. Neither scheduler substitutes for persisted application metadata.
