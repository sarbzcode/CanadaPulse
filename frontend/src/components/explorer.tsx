"use client";
import { useState } from "react";
import useSWR from "swr";
import { browserFetch, number, month, timestamp } from "@/lib/api";
import type { Labour, Filters, Headline } from "@/lib/types";
import { TrendChart } from "./charts";
import { Heading, Card, Panel, Notice } from "./ui";
const options = {
  revalidateOnFocus: false,
  dedupingInterval: 60000,
  errorRetryCount: 1,
};
const defaults = {
  geography: "Canada",
  indicator: "Unemployment rate",
  gender: "Total - Gender",
  age_group: "15 years and over",
  adjustment: "Seasonally adjusted",
  start_date: new Date().getUTCFullYear() - 5 + "-01-01",
  end_date: new Date().toISOString().slice(0, 10),
};
export function Explorer({
  mode,
}: {
  mode: "provinces" | "trends" | "explore";
}) {
  const [draft, setDraft] = useState(defaults),
    [filters, setFilters] = useState(defaults),
    [compare, setCompare] = useState(""),
    [page, setPage] = useState(0);
  const { data: choices, error: choiceError } = useSWR<Filters>(
    "/api/v1/filters",
    browserFetch,
    options,
  );
  const params = new URLSearchParams({ ...filters, limit: "1000" }),
    url = "/api/v1/labour/history?" + params;
  const { data, error, isLoading, mutate } = useSWR<Labour[]>(
    url,
    browserFetch,
    options,
  );
  const cp = new URLSearchParams({
    ...filters,
    geography: compare,
    limit: "1000",
  });
  const { data: comparison, error: comparisonError } = useSWR<Labour[]>(
    compare ? "/api/v1/labour/history?" + cp : null,
    browserFetch,
    options,
  );
  const { data: headline } = useSWR<Headline | null>(
    mode === "provinces"
      ? "/api/v1/labour/latest?geography=" +
          encodeURIComponent(filters.geography)
      : null,
    browserFetch,
    options,
  );
  const map = new Map(comparison?.map((r) => [r.date, r.value]));
  const chart =
    data?.map((r) => ({
      date: r.date,
      value: r.value,
      comparison: map.get(r.date) ?? null,
    })) || [];
  const title =
    mode === "provinces"
      ? "A closer look at every province."
      : mode === "trends"
        ? "Put the long view in focus."
        : "Explore the observations.";
  function update(key: string, value: string) {
    setDraft((s) => ({ ...s, [key]: value }));
  }
  function download() {
    if (!data) return;
    const fields = [
      "date",
      "geography",
      "indicator",
      "gender",
      "age_group",
      "adjustment",
      "value",
      "unit",
      "source_status",
    ] as const;
    const escape = (v: unknown) =>
      '"' + String(v ?? "").replaceAll('"', '""') + '"';
    const csv = [
      fields.join(","),
      ...data.map((r) => fields.map((k) => escape(r[k])).join(",")),
    ].join("\r\n");
    const u = URL.createObjectURL(
      new Blob([csv], { type: "text/csv;charset=utf-8" }),
    );
    const a = document.createElement("a");
    a.href = u;
    a.download =
      "canadapulse-" +
      filters.geography.toLowerCase().replaceAll(" ", "-") +
      ".csv";
    a.click();
    setTimeout(() => URL.revokeObjectURL(u), 1000);
  }
  return (
    <>
      <Heading title={title}>
        Compare like-for-like labour observations. Every value retains its
        source unit and reference month.
      </Heading>
      {choiceError && (
        <Notice error>
          Filter options could not be loaded. Check the data service and try
          again.
        </Notice>
      )}
      <form
        className="filters"
        onSubmit={(e) => {
          e.preventDefault();
          setFilters(draft);
          setPage(0);
        }}
      >
        {(
          [
            "geography",
            "indicator",
            ...(mode === "explore"
              ? ["gender", "age_group", "adjustment"]
              : []),
          ] as (keyof Filters)[]
        ).map((key) => (
          <label key={key}>
            {key.replace("_", " ").toUpperCase()}
            <select
              value={draft[key]}
              onChange={(e) => update(key, e.target.value)}
            >
              {(choices?.[key] || [defaults[key]]).map((value) => (
                <option key={value}>{value}</option>
              ))}
            </select>
          </label>
        ))}
        <label>
          FROM
          <input
            type="date"
            required
            value={draft.start_date}
            onChange={(e) => update("start_date", e.target.value)}
          />
        </label>
        <label>
          THROUGH
          <input
            type="date"
            required
            value={draft.end_date}
            onChange={(e) => update("end_date", e.target.value)}
          />
        </label>
        <button className="button primary" type="submit">
          Apply filters
        </button>
      </form>
      {mode === "provinces" && headline && (
        <>
          <p className="lead">
            Latest headline figures · {month(headline.reference_date)} · Total
            gender, ages 15+, seasonally adjusted. These cards use the latest
            month, independent of the history date filter.
          </p>
          <div className="metrics">
            <Card
              label="Unemployment rate"
              value={number(headline.unemployment_rate) + "%"}
              note={filters.geography}
            />
            <Card
              label="Employment"
              value={number(headline.employment, 0)}
              note="Persons"
            />
            <Card
              label="Employment rate"
              value={number(headline.employment_rate) + "%"}
              note="Seasonally adjusted"
            />
            <Card
              label="Participation rate"
              value={number(headline.participation_rate) + "%"}
              note="Seasonally adjusted"
            />
            <Card
              label="Employment change YoY"
              value={number(headline.yoy_employment_change_pct) + "%"}
              note="Exact prior-year month"
            />
          </div>
        </>
      )}
      {isLoading ? (
        <Notice>Loading selected observations…</Notice>
      ) : error ? (
        <Notice error>
          {error.message}{" "}
          <button className="button" onClick={() => mutate()}>
            Retry
          </button>
        </Notice>
      ) : (
        <>
          <Panel
            title={filters.indicator + " · " + filters.geography}
            subtitle={`${filters.gender} · ${filters.age_group} · ${filters.adjustment}`}
          >
            <label className="lead">
              Compare with{" "}
              <select
                className="button"
                value={compare}
                onChange={(e) => setCompare(e.target.value)}
              >
                <option value="">No comparison</option>
                {choices?.geography
                  .filter((g) => g !== filters.geography)
                  .map((g) => (
                    <option key={g}>{g}</option>
                  ))}
              </select>
            </label>
            {comparisonError && (
              <Notice error>Comparison data is unavailable.</Notice>
            )}
            <TrendChart
              data={chart}
              unit={data?.[0]?.unit || "Source units"}
              label={filters.geography}
              compareLabel={compare || undefined}
            />
            <p className="sources">
              Statistics Canada · Most recent selected observation loaded:{" "}
              {timestamp(data?.at(-1)?.loaded_at)}
            </p>
          </Panel>
          {mode === "explore" && (
            <Panel
              title="Behind the numbers"
              subtitle="Up to 1,000 monthly observations per view. CSV includes the full selected series."
            >
              <button
                className="button"
                disabled={!data?.length}
                onClick={download}
              >
                ↓ Export CSV
              </button>
              <div className="table-wrap">
                <table>
                  <thead>
                    <tr>
                      <th>Month</th>
                      <th>Geography</th>
                      <th>Indicator</th>
                      <th>Value</th>
                      <th>Unit</th>
                      <th>Source flag</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data
                      ?.slice()
                      .reverse()
                      .slice(page * 15, page * 15 + 15)
                      .map((r) => (
                        <tr key={r.date}>
                          <td>{r.date}</td>
                          <td>{r.geography}</td>
                          <td>{r.indicator}</td>
                          <td>{number(r.value)}</td>
                          <td>{r.unit}</td>
                          <td>{r.source_status || "—"}</td>
                        </tr>
                      ))}
                  </tbody>
                </table>
              </div>
              {!data?.length && (
                <p className="empty">No observations for these filters.</p>
              )}
              <div className="table-actions">
                <span>
                  {data?.length || 0} observations · Page {page + 1}
                </span>
                <div>
                  <button
                    className="button"
                    disabled={!page}
                    onClick={() => setPage((p) => p - 1)}
                  >
                    Previous
                  </button>
                  <button
                    className="button"
                    disabled={(page + 1) * 15 >= (data?.length || 0)}
                    onClick={() => setPage((p) => p + 1)}
                  >
                    Next
                  </button>
                </div>
              </div>
            </Panel>
          )}
        </>
      )}
    </>
  );
}
