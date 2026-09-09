"""Stream the canonical headline-scope labour observations to a Spark-readable CSV."""

import argparse
from pathlib import Path

from canadapulse.config import load_settings
from canadapulse.database.connection import connect


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("data/processed/spark_labour.csv"))
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with connect(load_settings().database) as c:
        c.execute("SET TRANSACTION READ ONLY")
        with (
            c.cursor() as cursor,
            args.output.open("wb") as output,
            cursor.copy(
                "COPY (SELECT date, geography, indicator, value, unit, pipeline_run_id "
                "FROM analytics.labour_observations WHERE gender='Total - Gender' "
                "AND age_group='15 years and over' AND adjustment='Seasonally adjusted') "
                "TO STDOUT WITH (FORMAT CSV, HEADER TRUE)"
            ) as copy,
        ):
            for block in copy:
                output.write(block)
    print(f"Exported source observations to {args.output}")


if __name__ == "__main__":
    main()
