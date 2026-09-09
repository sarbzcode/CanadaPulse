# Idempotent source revisions

## Context

Government observations can be republished. Hashing the entire row would make revised values look like new observations.

## Decision

Retain the existing source-key upsert design, excluding values from identity. Preserve raw payloads and latest run lineage. Measure inserted, revised and unchanged matches before loading.

## Alternatives

Append every download; delete and reload; maintain full bitemporal revision history.

## Consequences

Reruns do not inflate facts. This is a latest-observation store; deleted source rows and historical revisions require a deliberate future policy.
