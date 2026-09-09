"""Optional local/Databricks DataFrame demonstration over exported real observations."""

import argparse

from pyspark.sql import SparkSession, Window
from pyspark.sql import functions as F
from pyspark.sql.types import DateType, DecimalType, StringType, StructField, StructType


def transform(frame):
    """Compute calendar-aware changes without mixing geography, indicator or source units."""
    window = Window.partitionBy("geography", "indicator", "unit").orderBy("date")
    monthly = (
        frame.withColumn("year", F.year("date"))
        .withColumn("previous_date", F.lag("date").over(window))
        .withColumn("previous_value", F.lag("value").over(window))
        .withColumn(
            "monthly_change",
            F.when(
                F.add_months("previous_date", 1) == F.col("date"),
                F.col("value") - F.col("previous_value"),
            ),
        )
    )
    annual = monthly.groupBy("year", "geography", "indicator", "unit").agg(
        F.count("*").alias("observed_months"),
        F.count("value").alias("non_missing_months"),
        F.avg("value").alias("mean_observed_value"),
        F.min("date").alias("first_observation"),
        F.max("date").alias("last_observation"),
    )
    return monthly, annual


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--master", default="local[2]")
    parser.add_argument("--partitions", type=int, default=4)
    args = parser.parse_args()
    if args.partitions < 1:
        parser.error("partitions must be positive")
    spark = SparkSession.builder.master(args.master).appName("CanadaPulseHistory").getOrCreate()
    try:
        spark.conf.set("spark.sql.shuffle.partitions", args.partitions)
        schema = StructType(
            [
                StructField("date", DateType()),
                StructField("geography", StringType()),
                StructField("indicator", StringType()),
                StructField("value", DecimalType(18, 6)),
                StructField("unit", StringType()),
                StructField("pipeline_run_id", StringType()),
            ]
        )
        frame = (
            spark.read.option("header", True)
            .option("mode", "FAILFAST")
            .schema(schema)
            .csv(args.input)
        )
        if frame.filter("date IS NULL OR geography IS NULL OR indicator IS NULL").limit(1).count():
            raise ValueError("Input must include valid dates, geographies and indicators")
        if (
            frame.groupBy("date", "geography", "indicator", "unit")
            .count()
            .filter("count > 1")
            .limit(1)
            .count()
        ):
            raise ValueError("Duplicate observations would make the window calculation ambiguous")
        monthly, annual = transform(frame)
        monthly.repartition(args.partitions, "year").write.mode("errorifexists").partitionBy(
            "year", "geography"
        ).parquet(args.output + "/monthly")
        annual.write.mode("errorifexists").parquet(args.output + "/annual")
        print(f"Wrote {frame.count()} monthly observations and {annual.count()} annual groups")
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
