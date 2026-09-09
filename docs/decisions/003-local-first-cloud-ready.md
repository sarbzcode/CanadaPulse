# 003: Keep the Platform Local First

## Context

The project should demonstrate cloud-ready thinking without requiring paid infrastructure
for basic development or portfolio review.

## Decision

Keep Docker Compose and PostgreSQL as the primary local runtime. Document an Azure and
Databricks path separately.

## Alternatives

- Start directly with Azure services.
- Keep everything in local files.

## Consequences

The project stays reproducible for reviewers while leaving a credible path to Data Lake,
Databricks, Key Vault, monitoring, and Power BI integration.

