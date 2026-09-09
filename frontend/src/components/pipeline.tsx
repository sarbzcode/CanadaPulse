"use client";
import useSWR from "swr";
import { browserFetch, number, timestamp } from "@/lib/api";
import type { Pipeline, Run } from "@/lib/types";
import { Heading, Panel, Card, Notice } from "./ui";
const label = (s: string) =>
  s === "boc"
    ? "Bank of Canada"
    : s === "statcan"
      ? "Statistics Canada"
      : s === "warehouse"
        ? "dbt warehouse"
        : s;
export function PipelinePage() {
  const { data, error, isLoading, mutate } = useSWR<Pipeline>(
    "/api/v1/pipeline/status",
    browserFetch,
    { refreshInterval: 60000, revalidateOnFocus: false, errorRetryCount: 1 },
  );
  const { data: runs, error: runError } = useSWR<Run[]>(
    "/api/v1/pipeline/runs?limit=15",
    browserFetch,
    { refreshInterval: 60000, revalidateOnFocus: false, errorRetryCount: 1 },
  );
  return (
    <>
      <Heading
        title="From source to insight. Every run, visible."
        eyebrow="PIPELINE OBSERVABILITY"
      >
        Actual ingestion status, warehouse checks, and refresh history. This is
        a batch data platform; status is checked once per minute while this page
        is open.
      </Heading>
      {isLoading ? (
        <Notice>Checking the latest pipeline runs…</Notice>
      ) : error ? (
        <Notice error>
          {error.message}{" "}
          <button className="button" onClick={() => mutate()}>
            Retry
          </button>
        </Notice>
      ) : (
        data && (
          <>
            <div className="metrics">
              <Card
                label="Pipeline health"
                value={data.status}
                note="Based on latest outcomes and freshness"
              />
              <Card
                label="Quality checks"
                value={number(data.quality_checks, 0)}
                note="Measured in the latest source/warehouse runs"
              />
              <Card
                label="Failed checks"
                value={number(data.quality_failures, 0)}
                note="Not a historical lifetime total"
              />
            </div>
            <Notice>
              Last successful warehouse refresh:{" "}
              {timestamp(data.last_successful_refresh)}
            </Notice>
            <div className="grid-two">
              {data.sources.map((s) => (
                <Panel
                  key={s.source}
                  title={label(s.source)}
                  subtitle={"Last success: " + timestamp(s.last_successful_run)}
                >
                  <span
                    className={
                      "status-pill " + (s.status === "healthy" ? "" : "bad")
                    }
                  >
                    {s.status}
                  </span>
                  <div className="table-actions">
                    <span>{number(s.records_processed, 0)} observations</span>
                    <span>{number(s.duration_seconds, 2)} seconds</span>
                  </div>
                  <p className="sources">
                    Latest reference date:{" "}
                    {s.latest_reference_date || "Not recorded for this run"}
                  </p>
                </Panel>
              ))}
            </div>
            <Panel
              title="Measured data-quality checks"
              subtitle="Source coverage and integrity observations plus dbt assertions. Missing values are preserved, not invented."
            >
              <div className="quality-list">
                {data.quality_results.map((q, i) => (
                  <div className="quality-row" key={q.check_name + i}>
                    <div>
                      <strong>
                        {q.check_name.replace("test.canadapulse.", "")}
                      </strong>
                      <p>{q.expected_condition}</p>
                    </div>
                    <span
                      className={
                        "status-pill " + (q.status === "PASS" ? "" : "bad")
                      }
                    >
                      {q.status}
                    </span>
                  </div>
                ))}
              </div>
              {!data.quality_results.length && (
                <p className="empty">
                  No recorded checks yet. A successful tracked refresh will
                  populate this panel.
                </p>
              )}
            </Panel>
          </>
        )
      )}
      <Panel
        title="Recent pipeline runs"
        subtitle="Loaded includes inserted, revised, and unchanged observations reconciled by an upsert."
      >
        {runError ? (
          <Notice error>Run history is temporarily unavailable.</Notice>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Source</th>
                  <th>Started (UTC)</th>
                  <th>Status</th>
                  <th>Loaded</th>
                  <th>Inserted</th>
                  <th>Revised</th>
                  <th>Unchanged</th>
                  <th>Rejected</th>
                  <th>Duration</th>
                </tr>
              </thead>
              <tbody>
                {runs?.map((r) => (
                  <tr key={r.pipeline_run_id}>
                    <td>{label(r.source_name)}</td>
                    <td>{timestamp(r.started_at)}</td>
                    <td>
                      <span
                        className={
                          "status-pill " + (r.status === "SUCCESS" ? "" : "bad")
                        }
                      >
                        {r.status}
                      </span>
                    </td>
                    <td>{number(r.records_loaded, 0)}</td>
                    <td>{number(r.records_inserted, 0)}</td>
                    <td>{number(r.records_updated, 0)}</td>
                    <td>{number(r.records_unchanged, 0)}</td>
                    <td>{number(r.records_rejected, 0)}</td>
                    <td>{number(r.duration_seconds, 2)}s</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Panel>
    </>
  );
}
