# 002: Use Layered ELT

## Context

The platform needs to preserve source traceability while producing BI-ready models.

## Decision

Python ingestion writes validated source-aligned records to `raw` and dbt owns staging,
intermediate, and analytics transformations.

## Alternatives

- Transform everything in Python before loading.
- Put business logic in Airflow DAGs.

## Consequences

This separation makes lineage, testing, and interview explanation clearer. It also keeps
orchestration focused on scheduling instead of transformation logic.

