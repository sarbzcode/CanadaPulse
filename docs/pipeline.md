# Pipeline behavior

The implemented flow is download -> validate -> temporary COPY table -> upsert raw
observations -> finalize source run metadata -> dbt build and tests -> curated analytics -> API.
Run `python -m canadapulse.cli refresh` from the repository root for the complete flow.
`ingest` still runs only source ingestion; `warehouse` rebuilds and tests the warehouse separately.

Downloads retry up to three times and use a 120-second socket timeout. A temporary `.part`
file is renamed only after the transfer succeeds. Use `--reuse-cache` only for deliberate
offline replay; normal runs fetch fresh data. A PostgreSQL session advisory lock serializes
runs of the same source.

Each source has its own atomic transaction. The RUNNING metadata record is committed before
loading. Source data and SUCCESS metadata commit together. An invalid date, invalid numeric
value, missing required structure, duplicate source key within the download, or empty selected
response fails the source transaction. Existing observations remain intact and FAILED metadata
is recorded separately. A failed second source does not roll back an already successful first
source. A forcibly killed process can leave a RUNNING metadata row requiring investigation.

Bank of Canada loads daily V39079 observations on or after the requested start date. Statistics
Canada loads monthly Estimate rows on or after that date, excluding standard errors and source
change statistics. Rows intentionally outside this scope are not rejected rows and are not
included in extracted counts. Missing labour values remain null, with source status preserved.
Malformed observations fail the run rather than silently creating incomplete dashboard data.

`records_loaded` counts observations successfully upserted, including existing observations
refreshed by a rerun. It is not a count of newly inserted records. On rollback, loaded is zero;
extracted reports how many selected observations were encountered before failure, and rejected
counts malformed observations detected before stopping.

Bank of Canada identity is date plus series. Labour identity is a SHA-256 hash of full-table
PID, reference period, vector, and coordinate. Values are excluded from the identity so source
revisions update the same record. Rows absent from a later download are not deleted, and old
versions of revised values are not archived. The full CSV is streamed, never extracted to disk.

The default start is 2015-01-01. Extending history uses `--start-date`; narrowing the date does
not remove previously loaded data. Ingestion currently supports one enabled BoC series, as
configured in the repository, and the Statistics Canada labour dataset.

Each successful source run records inserted, updated and unchanged observations separately.
Unchanged means the existing source payload matched; it is not a claim about rows skipped by
PostgreSQL. Five quality results record selected-row presence, key uniqueness, load reconciliation,
missing-value rate and reference-period coverage. Null labour values are retained rather than
converted to zero. A failed source transaction rolls back its quality results with its data.

The warehouse preserves source lineage through staging, intermediate models and dimensional facts.
Its tracked run stores actual dbt test results and the combined fact-row count. An advisory lock
serializes warehouse refreshes. dbt replaces each table atomically, but publication across all models
is not a single transaction: concurrent readers can briefly observe models from different refreshes.
A failed test marks the warehouse run failed; it does not roll back models already built.

The versioned API and Next.js website query curated models. The original local explorer and its
legacy routes remain available. Public status reports actual run metadata and freshness, excluding
internal exception details. See [warehouse](warehouse.md), [orchestration](orchestration.md), and
[deployment](deployment.md) for dbt, scheduler and hosting instructions.
