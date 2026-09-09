"use client";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  LineChart,
  Line,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  BarChart,
  Bar,
} from "recharts";
import { month, number } from "@/lib/api";
export type Point = {
  date: string;
  value: number | null;
  comparison?: number | null;
};
export function TrendChart({
  data,
  unit,
  label,
  compareLabel,
  step = false,
}: {
  data: Point[];
  unit: string;
  label: string;
  compareLabel?: string;
  step?: boolean;
}) {
  if (!data.length)
    return <p className="empty">No observations match this selection.</p>;
  return (
    <figure aria-label={label + " over time, in " + unit}>
      <div className="chart-box">
        <ResponsiveContainer width="100%" height="100%" minWidth={0}>
          {compareLabel ? (
            <LineChart data={data}>
              <CartesianGrid stroke="#e8eee9" strokeDasharray="3 5" />
              <XAxis dataKey="date" tickFormatter={month} minTickGap={40} />
              <YAxis width={65} tickFormatter={(v) => number(Number(v), 0)} />
              <Tooltip
                labelFormatter={(v) => String(v)}
                formatter={(v, name) => [number(Number(v)) + " " + unit, name]}
              />
              <Line
                name={label}
                dataKey="value"
                stroke="#14785f"
                dot={false}
                connectNulls={false}
              />
              <Line
                name={compareLabel}
                dataKey="comparison"
                stroke="#677bb0"
                dot={false}
                connectNulls={false}
              />
            </LineChart>
          ) : (
            <AreaChart data={data}>
              <CartesianGrid stroke="#e8eee9" strokeDasharray="3 5" />
              <XAxis dataKey="date" tickFormatter={month} minTickGap={40} />
              <YAxis width={65} tickFormatter={(v) => number(Number(v), 0)} />
              <Tooltip
                labelFormatter={(v) => String(v)}
                formatter={(v) => [number(Number(v)) + " " + unit, label]}
              />
              <Area
                type={step ? "stepAfter" : "linear"}
                dataKey="value"
                name={label}
                stroke="#14785f"
                strokeWidth={2}
                fill="#e6f1ea"
                connectNulls={false}
                isAnimationActive={false}
              />
            </AreaChart>
          )}
        </ResponsiveContainer>
      </div>
      <figcaption>
        {label}
        {compareLabel ? " (green) · " + compareLabel + " (blue)" : ""} · {unit}{" "}
        · Missing values remain gaps.
      </figcaption>
    </figure>
  );
}
export function ProvinceChart({
  data,
}: {
  data: { geography: string; unemployment_rate: number | null }[];
}) {
  if (!data.length)
    return <p className="empty">No provincial data available.</p>;
  return (
    <figure aria-label="Provincial unemployment rates in percent">
      <div className="chart-box province-chart">
        <ResponsiveContainer width="100%" height="100%" minWidth={0}>
          <BarChart
            data={data}
            layout="vertical"
            margin={{ left: 5, right: 20 }}
          >
            <XAxis type="number" unit="%" />
            <YAxis
              type="category"
              dataKey="geography"
              width={145}
              tick={{ fontSize: 11 }}
            />
            <Tooltip
              formatter={(v) => [number(Number(v)) + "%", "Unemployment rate"]}
            />
            <Bar
              dataKey="unemployment_rate"
              fill="#629981"
              radius={[0, 4, 4, 0]}
              isAnimationActive={false}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>
      <figcaption>
        One reference month · Total gender · Ages 15+ · Seasonally adjusted.
      </figcaption>
    </figure>
  );
}
