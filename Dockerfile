FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
COPY sql ./sql
COPY config ./config
COPY warehouse ./warehouse
RUN pip install --no-cache-dir -e '.[warehouse]' \
    && useradd --create-home appuser && chown -R appuser:appuser /app
USER appuser
EXPOSE 8000
CMD ["python", "-m", "canadapulse.api.server"]
