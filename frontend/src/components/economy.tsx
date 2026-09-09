"use client";
import { useState } from "react";
import useSWR from "swr";
import { browserFetch, number, timestamp } from "@/lib/api";
import type { Rate } from "@/lib/types";
import { Heading, Panel, Card, Notice } from "./ui";
import { TrendChart } from "./charts";
export function Economy() {
  const [start, setStart] = useState("2015-01-01");
  const { data, error, isLoading, mutate } = useSWR<Rate[]>(
    "/api/v1/economy/interest-rates?limit=20000&start_date=" + start,
    browserFetch,
    { revalidateOnFocus: false, errorRetryCount: 1 },
  );
  return (
    <>
      <Heading title="The price of borrowing, over time.">
        Explore the Bank of Canada&apos;s target overnight rate. These are
        observed business-daily rates, not monthly averages.
      </Heading>
      <div className="filters">
        <label>
          HISTORY FROM
          <input
            type="date"
            value={start}
            onChange={(e) => {
              if (e.target.value) setStart(e.target.value);
            }}
          />
        </label>
      </div>
      {isLoading ? (
        <Notice>Loading interest-rate history…</Notice>
      ) : error ? (
        <Notice error>
          {error.message}{" "}
          <button className="button" onClick={() => mutate()}>
            Retry
          </button>
        </Notice>
      ) : (
        <>
          <div className="metrics">
            <Card
              label="Latest rate in range"
              value={data?.length ? number(data.at(-1)?.rate, 2) + "%" : "—"}
              note={data?.at(-1)?.date || "No observations"}
            />
            <Card
              label="Daily observations"
              value={number(data?.length, 0)}
              note="Official series V39079"
            />
          </div>
          <Panel
            title="Target overnight rate"
            subtitle="Percent · Bank of Canada"
          >
            <TrendChart
              data={data?.map((r) => ({ date: r.date, value: r.rate })) || []}
              label="Policy rate"
              unit="Percent"
              step
            />
            <p className="sources">
              Data loaded: {timestamp(data?.at(-1)?.loaded_at)}
            </p>
          </Panel>
          <Notice>
            Trend alignment or correlation does not imply causation between
            interest rates and employment. Daily rates and monthly labour
            observations have different frequencies.
          </Notice>
        </>
      )}
    </>
  );
}
