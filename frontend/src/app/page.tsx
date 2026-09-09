import Link from "next/link";
import { Heading, Card, Panel, Notice, Sources } from "@/components/ui";
import { TrendChart, ProvinceChart } from "@/components/charts";
import { serverFetch, number, month } from "@/lib/api";
import type { Summary, Labour, Headline, Rate } from "@/lib/types";
export const revalidate = 300;
export default async function Overview() {
  let data: [Summary, Labour[], Labour[], Headline[], Rate[]] | null = null;
  try {
    data = await Promise.all([
      serverFetch<Summary>("/api/v1/dashboard/summary"),
      serverFetch<Labour[]>(
        "/api/v1/labour/history?indicator=Unemployment%20rate",
      ),
      serverFetch<Labour[]>("/api/v1/labour/history?indicator=Employment"),
      serverFetch<Headline[]>("/api/v1/labour/compare"),
      serverFetch<Rate[]>("/api/v1/economy/interest-rates"),
    ]);
  } catch {}
  const s = data?.[0],
    l = s?.labour;
  return (
    <>
      <Heading title="CanadaPulse">
        Canadian Economic & Labour Market Intelligence. Explore Canadian
        labour-market and economic trends using processed data from Statistics
        Canada and the Bank of Canada.
      </Heading>
      {!data ? (
        <Notice error>
          The data service is temporarily unavailable or awaiting its first
          deployment. <Link href="/pipeline">Check pipeline status</Link> or
          return shortly.
        </Notice>
      ) : (
        <>
          <div className="metrics">
            <Card
              label="Unemployment rate"
              value={
                l?.unemployment_rate == null
                  ? "—"
                  : number(l.unemployment_rate) + "%"
              }
              note={l ? month(l.reference_date) + " · Canada" : "Not available"}
            />
            <Card
              label="Employment"
              value={number(l?.employment, 0)}
              note="Persons · Total gender · Ages 15+"
            />
            <Card
              label="Participation rate"
              value={
                l?.participation_rate == null
                  ? "—"
                  : number(l.participation_rate) + "%"
              }
              note="Seasonally adjusted"
            />
            <Card
              label="Employment rate"
              value={
                l?.employment_rate == null
                  ? "—"
                  : number(l.employment_rate) + "%"
              }
              note="Seasonally adjusted"
            />
            <Card
              label="Overnight rate"
              value={
                s?.interest_rate ? number(s.interest_rate.rate, 2) + "%" : "—"
              }
              note={
                s?.interest_rate
                  ? "As of " + s.interest_rate.date
                  : "No rate available"
              }
            />
          </div>
          {!l && (
            <Notice>No headline observations have been published yet.</Notice>
          )}
          <Sources updated={s?.warehouse_refreshed_at} />
          <div className="grid-two">
            <div>
              <Panel
                title="Canada's unemployment trend"
                subtitle="Five-year view · Percent · Total gender, ages 15+, seasonally adjusted"
              >
                <TrendChart
                  data={data[1].map((r) => ({ date: r.date, value: r.value }))}
                  unit="Percent"
                  label="Unemployment rate"
                />
              </Panel>
              <Panel
                title="Employment, over time"
                subtitle="Source values in thousands of persons"
              >
                <TrendChart
                  data={data[2].map((r) => ({ date: r.date, value: r.value }))}
                  unit="Persons in thousands"
                  label="Employment"
                />
              </Panel>
            </div>
            <div>
              <Panel
                title="Across the provinces"
                subtitle={
                  data[3][0]
                    ? month(data[3][0].reference_date) + " · Unemployment rate"
                    : "No comparison available"
                }
              >
                <ProvinceChart data={data[3]} />
                <Link className="button" href="/provinces">
                  Explore a province →
                </Link>
              </Panel>
              <Panel
                title="Make the data your own"
                subtitle="Choose a geography, demographic, indicator and date range."
              >
                <p className="lead">
                  Inspect the source observations and export a CSV for your own
                  analysis.
                </p>
                <Link className="button primary mt-5" href="/explore">
                  Open data explorer →
                </Link>
              </Panel>
            </div>
          </div>
          <Panel
            title="The policy rate, over time"
            subtitle="Bank of Canada · Daily observations · Trends do not imply causation"
          >
            <TrendChart
              data={data[4].map((r) => ({ date: r.date, value: r.rate }))}
              unit="Percent"
              label="Target overnight rate"
              step
            />
          </Panel>
        </>
      )}
    </>
  );
}
