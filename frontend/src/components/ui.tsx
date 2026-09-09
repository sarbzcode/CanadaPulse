import type { ReactNode } from "react";
import { timestamp } from "@/lib/api";
export function Heading({
  eyebrow = "CANADIAN ECONOMIC INTELLIGENCE",
  title,
  children,
}: {
  eyebrow?: string;
  title: string;
  children: ReactNode;
}) {
  return (
    <header className="page-heading">
      <p className="eyebrow">{eyebrow}</p>
      <h1>{title}</h1>
      <p className="lead">{children}</p>
    </header>
  );
}
export function Card({
  label,
  value,
  note,
}: {
  label: string;
  value: string;
  note: string;
}) {
  return (
    <article className="metric">
      <p>{label}</p>
      <strong>{value}</strong>
      <small>{note}</small>
    </article>
  );
}
export function Notice({
  error = false,
  children,
}: {
  error?: boolean;
  children: ReactNode;
}) {
  return (
    <div
      className={error ? "notice error" : "notice"}
      role={error ? "alert" : "status"}
    >
      {children}
    </div>
  );
}
export function Panel({
  title,
  subtitle,
  children,
}: {
  title: string;
  subtitle?: string;
  children: ReactNode;
}) {
  return (
    <section className="panel">
      <div className="panel-heading">
        <h2>{title}</h2>
        {subtitle && <p>{subtitle}</p>}
      </div>
      {children}
    </section>
  );
}
export function Sources({ updated }: { updated?: string | null }) {
  return (
    <div className="sources">
      <span>
        Sources:{" "}
        <a href="https://www.statcan.gc.ca/en/developers/wds">
          Statistics Canada
        </a>{" "}
        · <a href="https://www.bankofcanada.ca/valet/docs">Bank of Canada</a>
      </span>
      <span>Warehouse refresh: {timestamp(updated)}</span>
    </div>
  );
}
