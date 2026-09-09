"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Activity,
  ArrowUpRight,
  BarChart3,
  Database,
  Globe2,
  Info,
  LayoutDashboard,
  TrendingUp,
} from "lucide-react";
import { apiOrigin } from "@/lib/api";
const links = [
  ["/", "Overview", LayoutDashboard],
  ["/provinces", "Provinces", Globe2],
  ["/trends", "Labour trends", TrendingUp],
  ["/economy", "The economy", BarChart3],
  ["/explore", "Data explorer", Database],
  ["/pipeline", "Pipeline health", Activity],
  ["/about", "About the project", Info],
] as const;
export function Navigation() {
  const path = usePathname();
  return (
    <aside className="sidebar">
      <Link href="/" className="brand">
        <span className="brand-icon">
          <Activity size={20} />
        </span>
        CanadaPulse
      </Link>
      <p className="nav-label">ECONOMIC INTELLIGENCE</p>
      <nav aria-label="Main navigation">
        {links.map(([url, label, Icon]) => (
          <Link
            key={url}
            href={url}
            className={path === url ? "nav-link active" : "nav-link"}
            aria-current={path === url ? "page" : undefined}
          >
            <Icon size={17} />
            {label}
          </Link>
        ))}
      </nav>
      <div className="sidebar-bottom">
        <a
          href="https://github.com/sarbzcode/CanadaPulse"
          target="_blank"
          rel="noreferrer"
        >
          View on GitHub <ArrowUpRight size={14} />
        </a>
        {apiOrigin && (
          <a href={apiOrigin + "/docs"} target="_blank" rel="noreferrer">
            API documentation <ArrowUpRight size={14} />
          </a>
        )}
        <p>
          Independent insight.
          <br />
          Official Canadian data.
        </p>
      </div>
    </aside>
  );
}
