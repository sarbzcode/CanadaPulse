# Separate public frontend and typed API

## Context

The original HTML dashboard works and should remain useful while the project gains an employer-facing website.

## Decision

Keep the MVP at the API root. Add Next.js with seven routes against a versioned Pydantic API over dbt marts. Cache the overview and bound interactive payloads.

## Alternatives

Replace the MVP entirely; use Power BI as the only public frontend; expose raw SQL to the browser.

## Consequences

Existing functionality remains available. Public views have source dates and honest failure states. The frontend and API can deploy independently with explicit CORS.
