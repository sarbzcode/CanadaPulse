# Dimensional warehouse and stable grain

## Context

The raw labour data has demographic, adjustment, measure, unit and source-series dimensions that must survive analytical joins.

## Decision

Use tested date/geography/indicator/series dimensions and facts. Preserve source identity and all labour dimensions. Derive geography membership from observed data, enriching descriptive metadata with a seed.

## Alternatives

A single flat table is simpler for one chart; a narrowly pivoted fact would lose valid source detail.

## Consequences

The star schema supports BI and relationship tests. Serving marts denormalize it for fast API reads. Keys are deterministic JSON-array hashes or YYYYMMDD date integers.
