FROM apache/airflow:3.3.1-python3.12
USER root
WORKDIR /opt/canadapulse
COPY --chown=airflow:root pyproject.toml README.md ./
COPY --chown=airflow:root src ./src
COPY --chown=airflow:root sql ./sql
COPY --chown=airflow:root config ./config
COPY --chown=airflow:root warehouse ./warehouse
COPY --chown=airflow:root airflow/dags /opt/airflow/dags
USER airflow
RUN pip install --no-cache-dir "apache-airflow==3.3.1" -e '.[warehouse]'
