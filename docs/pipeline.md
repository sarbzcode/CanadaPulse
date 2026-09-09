# Pipeline behavior

The implemented flow is download -> validate -> temporary COPY table -> upsert raw
observations -> finalize run metadata. SQL analytics views expose committed observations.
Run `python -m canadapulse.cli ingest` from the repository root.

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

The local dashboard and API are implemented. dbt and Airflow remain future extensions. For
scheduling instructions and the API routes, see ../README.md.
