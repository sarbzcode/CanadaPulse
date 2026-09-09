# Full rebuilds and serving indexes

## Context

The measured dataset fits a relational database and revisions can affect historical months.

## Decision

Use staging/intermediate views and rebuilt dimension/fact/mart tables. Index actual series filters and date-based comparisons. Record dbt outcomes and reconcile facts to raw sources.

## Alternatives

Incremental timestamp watermarks, Redis caches, or a distributed warehouse before measurements justify them.

## Consequences

Rebuilds are simple and revision-safe but consume storage and are transactional per model, not globally atomic. A future deployment can add staged publication if partial-refresh visibility becomes material.
