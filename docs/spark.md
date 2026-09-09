# Optional Spark demonstration

The main dataset fits PostgreSQL. Spark is not required for ingestion, dbt, API or the website.
This separate job demonstrates DataFrame transformations, explicit schemas, calendar-aware
windows, aggregations, shuffle partition control and partitioned Parquet over real exported
data. It does not claim the current workload needs a distributed cluster.

```bash
python scripts/export_spark_input.py
python -m pip install -r spark/requirements.txt
python spark/jobs/historical_labour_transform.py --input data/processed/spark_labour.csv --output spark/output/run-001
```

Use a Spark-compatible Java runtime (Java 17 is the tested container baseline), or run in
Linux/Databricks. Native Windows Hadoop file operations may require extra runtime setup.
The input is the canonical total-gender, age-15+, seasonally-adjusted serving slice; source
units and run lineage are preserved. Duplicate identities are rejected before windowing.
MoM changes require consecutive calendar months. Annual means are means of observed values,
not official annual releases; observed/non-missing month counts reveal incomplete years.

Output is partitioned by year/geography for common time and region reads. Four shuffle
partitions suit the small local demo; tune this for actual file sizes and cluster resources.
The job refuses to overwrite an existing run directory. On Databricks, install the project
dependencies, use an ADLS/DBFS input URI, set an appropriate master/cluster configuration,
and choose Delta output as an explicitly reviewed extension. Do not run a second production
transformation with different metric definitions alongside dbt without reconciliation tests.

Spark becomes useful when historical archives or additional datasets exceed one machine's
practical processing capacity, or when a lakehouse is already the organization standard.
For the current platform, SQL/dbt is simpler and faster to operate.
