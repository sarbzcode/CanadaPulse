"""Command line interface for local development operations."""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from datetime import date

from canadapulse.config import load_settings
from canadapulse.logging_config import configure_logging
from canadapulse.services.pipeline_service import PipelineService


def build_parser() -> argparse.ArgumentParser:
    """Build the CanadaPulse CLI parser."""

    parser = argparse.ArgumentParser(prog="canadapulse")
    subcommands = parser.add_subparsers(dest="command", required=True)

    subcommands.add_parser("config", help="Print redacted runtime configuration.")
    subcommands.add_parser("status", help="Check application and PostgreSQL connectivity.")
    subcommands.add_parser("init-db", help="Apply database schemas and analytics views.")
    subcommands.add_parser("warehouse", help="Build/test dbt and record quality results.")
    refresh = subcommands.add_parser("refresh", help="Ingest both sources and build/test dbt.")
    refresh.add_argument("--reuse-cache", action="store_true")
    ingest = subcommands.add_parser("ingest", help="Download and load official observations.")
    ingest.add_argument("--source", choices=["all", "boc", "statcan"], default="all")
    ingest.add_argument("--start-date", type=date.fromisoformat, default=date(2015, 1, 1))
    ingest.add_argument("--reuse-cache", action="store_true")
    serve = subcommands.add_parser("serve", help="Start the local dashboard and read-only API.")
    serve.add_argument("--port", type=int)
    serve.add_argument("--host")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CanadaPulse CLI."""

    parser = build_parser()
    args = parser.parse_args(argv)

    settings = load_settings()
    configure_logging(settings.log_level)

    if args.command in {"warehouse", "refresh"}:
        from canadapulse.ingestion.pipelines import initialize, run_source
        from canadapulse.services.warehouse_service import refresh_warehouse

        initialize(settings)
        if args.command == "refresh":
            for source in ("boc", "statcan"):
                run_source(settings, source, date(2015, 1, 1), args.reuse_cache)
        print(json.dumps(refresh_warehouse(settings), default=str))
        return 0

    if args.command in {"init-db", "ingest"}:
        from canadapulse.ingestion.pipelines import initialize, run_source

        initialize(settings)
        if args.command == "ingest":
            sources = ["boc", "statcan"] if args.source == "all" else [args.source]
            results = []
            for source in sources:
                results.append(run_source(settings, source, args.start_date, args.reuse_cache))
            print(json.dumps(results, indent=2))
        else:
            print("Database schemas and analytics views ready.")
        return 0

    if args.command == "serve":
        import uvicorn

        uvicorn.run(
            "canadapulse.api.app:app",
            host=args.host or settings.api_host,
            port=args.port or settings.api_port,
        )
        return 0

    if args.command == "config":
        print(json.dumps(settings.redacted(), indent=2, sort_keys=True))
        return 0

    if args.command == "status":
        status = PipelineService(settings).status()
        payload = {
            "service_version": status.service_version,
            "environment": status.environment,
            "database": {
                "ok": status.database.ok,
                "message": status.database.message,
                "latency_ms": status.database.latency_ms,
            },
        }
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0 if status.database.ok else 1

    parser.error(f"Unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
