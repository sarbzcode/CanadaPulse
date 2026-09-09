# 001: Use PostgreSQL for Local Warehouse

## Context

CanadaPulse needs a realistic relational warehouse that runs locally and supports raw data,
analytics models, metadata, constraints, indexes, and API queries.

## Decision

Use PostgreSQL as the local warehouse and operational metadata store.

## Alternatives

- SQLite: easy locally, but weaker fit for warehouse schemas and production-style SQL.
- Cloud warehouse: valuable later, but it would add cost and setup friction too early.

## Consequences

PostgreSQL gives the project credible database engineering surface area while remaining easy
to run through Docker Compose.

