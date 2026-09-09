import { Heading, Panel } from "@/components/ui";
export const metadata = { title: "About CanadaPulse" };
export default function About() {
  return (
    <>
      <Heading title="Public data. An inspectable journey.">
        CanadaPulse brings official labour and monetary-policy observations into
        a tested analytical warehouse and an accessible exploration experience.
      </Heading>
      <Panel title="The data lifecycle">
        <div
          className="architecture"
          aria-label="Sources to Python ingestion to PostgreSQL to dbt warehouse to FastAPI to Next.js"
        >
          {[
            "Official sources",
            "Python ingestion",
            "PostgreSQL raw",
            "dbt warehouse",
            "FastAPI",
            "Next.js",
          ].map((name, i) => (
            <div className="flex items-center gap-3" key={name}>
              {i > 0 && <b>→</b>}
              <span>{name}</span>
            </div>
          ))}
        </div>
        <p className="lead">
          GitHub Actions can schedule ingestion and run validation. Airflow
          provides an alternative orchestration path. Run status and
          data-quality checks remain queryable alongside the data.
        </p>
      </Panel>
      <div className="grid-two">
        <Panel title="Why this project exists">
          <div className="prose">
            <p>
              Public data is useful only when its definitions, units, lineage,
              and freshness are understandable. CanadaPulse is a Computer
              Science portfolio project built to demonstrate the complete data
              lifecycle, from external APIs to analytical models and public
              products.
            </p>
            <p>
              It emphasizes repeatable imports, source revisions, dimensional
              modelling, SQL tests, and honest operational status rather than
              unsupported scale claims.
            </p>
          </div>
        </Panel>
        <Panel title="Engineering decisions">
          <div className="prose">
            <p>
              PostgreSQL supports local development and hosted deployment. dbt
              keeps transformations, tests and lineage together. Deterministic
              keys preserve identity across revisions. Read-only FastAPI queries
              serve bounded datasets, while Next.js renders an independent
              public interface.
            </p>
            <p>
              Source values and suppression flags remain intact. Headline
              employment counts are converted from thousands to persons, and
              rate changes use percentage points.
            </p>
          </div>
        </Panel>
      </div>
      <Panel title="Sources and transparency">
        <div className="prose">
          <p>
            <a href="https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1410028701">
              Statistics Canada table 14-10-0287
            </a>{" "}
            supplies monthly labour observations. The{" "}
            <a href="https://www.bankofcanada.ca/valet/docs">
              Bank of Canada Valet API
            </a>{" "}
            supplies daily target overnight rates.
          </p>
          <p>
            CanadaPulse is independent and is not affiliated with these
            institutions or the Government of Canada. Trend comparisons do not
            establish causation.
          </p>
          <p>
            <a href="https://github.com/sarbzcode/CanadaPulse">
              Inspect the source, architecture, tests and deployment
              instructions on GitHub →
            </a>
          </p>
        </div>
      </Panel>
    </>
  );
}
