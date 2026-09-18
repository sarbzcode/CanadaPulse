# Public deployment

Status: **READY FOR DEPLOYMENT configuration; no public application URL has been verified.**
Do not confuse the running local dashboard with a public deployment.

## 1. Hosted PostgreSQL (Neon or compatible PostgreSQL)

Create a database and retain its PostgreSQL connection URL privately. The application accepts
DATABASE_URL with URL-encoded credentials and SSL options. Use sslmode=require or stronger.
For ingestion/dbt use a direct connection rather than transaction pooling: source jobs use
session advisory locks and temporary tables. The public API uses short read-only transactions.

Set DATABASE_URL in your private environment, install `.[warehouse]`, then run:

```bash
python -m canadapulse.cli init-db
python -m canadapulse.cli refresh
```

This initializes existing/new schemas, loads official data, builds the warehouse, executes
its tests, and records quality results. A narrow `ingest` command alone does not refresh dbt.
Allow several minutes for the full source archive. Plan database storage using measured sizes;
raw JSON payloads plus facts/indexes may exceed some free-tier quotas. No cloud cost is assumed.

Use a separate read-only database login for the public API. After creating that login through
your provider, grant CONNECT on the database, USAGE on analytics/warehouse/metadata, and SELECT
on their tables. If serving the preserved legacy explorer, also grant USAGE/SELECT on raw.
The ingestion owner should set ALTER DEFAULT PRIVILEGES for these schemas so dbt's replacement
tables retain reader access. Do not grant the API role CREATE, INSERT, UPDATE, or DELETE.
The application also enforces transaction-level read-only access as defense in depth.

## 2. Render API

Connect this GitHub repository and use the root Dockerfile or render.yaml blueprint. Configure:

- DATABASE_URL: private hosted database reader URL, with SSL.
- ENVIRONMENT: production.
- CORS_ORIGINS: exact Vercel origin(s), comma separated, no wildcard or trailing slash.
- API_HOST: 0.0.0.0.
- PORT: supplied by the platform; the server honors it.

Start command is `python -m canadapulse.api.server`. Health path is `/health`. API documentation
is `/docs` and `/redoc`. No ingestion runs during a web request or API startup. Apply migrations
and a successful dbt build before enabling public traffic. The original HTML explorer stays
available at the API root; the public Next.js website is a separate service.

## 3. Vercel frontend

Import the repository with root directory `frontend`, framework Next.js. Set
NEXT_PUBLIC_API_URL to the actual HTTPS Render origin. Optionally set FRONTEND_API_URL to a
server-reachable API origin for server rendering. These values are public origins, never database
credentials. Install/build commands are `npm ci` and `npm run build`. Redeploy after changing
NEXT_PUBLIC_API_URL because Next.js embeds it in browser assets.

The checked-in `frontend/vercel.json` explicitly selects Next.js and its `.next` build output.
Keep the Vercel project's Root Directory set to `frontend` so this configuration is read.
If an earlier deployment reports `No Output Directory named "public" found`, remove the
`public` Output Directory override in Vercel settings and redeploy the latest commit.
Do not create an empty `public` directory to work around this error.

### Render starts but health checks return 503

A successful Docker build and `Application startup complete` mean the server started;
they do not confirm database connectivity or warehouse initialization. The `/health`
endpoint queries PostgreSQL and the metadata tables. Diagnose using the public endpoints:

- `/api/health` returns 503: check Render's `DATABASE_URL`, database availability, and SSL.
  Paste the raw connection string without Markdown backslashes or surrounding quotes.
- `/api/health` returns 200 but `/health` returns 503: check that the metadata tables
  have been initialized and that the API database role can read them.
- Both return 200 but dashboard requests fail: check the dbt build and reader permissions
  on the serving tables. A degraded health response can also mean data is not loaded or stale.

For a new hosted database, run the initialization and full refresh from section 1 using
its private direct writer connection, then redeploy the API if its settings changed.
The local Docker database is separate from the hosted database. Keep `/health` as the
Render health check; changing it to a static route would hide the database failure.
An initial `HEAD /` response of 405 is separate from the failing `/health` checks.

After Vercel assigns the real website domain, add its exact origin to the API's CORS_ORIGINS.
Preview deployments require explicit allowed origins; do not allow every *.vercel.app origin.
The homepage revalidates server-fetched data; interactive filters use bounded API responses.

## 4. GitHub Actions

Python and dbt CI use disposable PostgreSQL and synthetic fixtures, never production secrets or
live government requests. Frontend CI compiles independently of a reachable production API.

For scheduled production refresh, set repository secret DATABASE_URL to the **writer/direct**
connection, and repository variable ENABLE_PRODUCTION_REFRESH=true. The workflow is disabled
unless explicitly enabled. Schedule the Bank of Canada on weekdays; Statistics Canada weekly
and around the monthly release window as documented in the workflow. Never run Airflow and
GitHub schedules simultaneously against the same deployment. GitHub concurrency plus database
session locks serialize overlapping work. A failed dbt build produces a failed workflow and
tracked warehouse run. Configure GitHub failure notifications for the repository owner.

## 5. Verification

1. `/health` responds without infrastructure details.
2. `/api/v1/dashboard/summary` has non-null data with source dates.
3. `/api/v1/pipeline/status` reports actual successful source/warehouse refreshes.
4. `/docs` lists Labour, Economy, Pipeline and System routes.
5. Website loads on desktop/mobile and handles API downtime without raw exceptions.
6. Browser requests succeed from the configured frontend origin.
7. Schedule runs successfully using writer credentials; API reader cannot write.

Only after these checks add the real website and API URLs to README. Hosting accounts,
credentials, domain selection and any provider billing approval must be supplied externally.

## Operational limits

This is a batch platform. Source extraction and warehouse refresh are distinct. Raw loads are
atomic per source. dbt table replacements are atomic per model, not one transaction for the
entire graph; during a build users may briefly see different model refresh times. Schedule
refreshes at low-traffic times and inspect failed runs before treating a refresh as published.
A killed process may leave a RUNNING record; investigate before changing its status. Free
hosting cold starts and platform quotas are provider-dependent, not an uptime guarantee.

References: [Neon connections](https://neon.com/docs/connect/connect-from-any-app),
[Render FastAPI](https://render.com/docs/deploy-fastapi),
[Next.js deployment](https://nextjs.org/docs/app/getting-started/deploying).
