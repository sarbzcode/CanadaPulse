"""Public contracts deliberately exclude payloads, connection details and error traces."""

from datetime import date, datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field


class LabourObservation(BaseModel):
    date: date
    geography: str
    indicator: str
    gender: str
    age_group: str
    adjustment: str
    value: float | None
    unit: str
    scalar_factor: str
    source_status: str | None = None
    loaded_at: datetime


class InterestObservation(BaseModel):
    date: date
    series_code: str
    series_name: str
    rate: float
    loaded_at: datetime


class Geography(BaseModel):
    geography_name: str
    geography_type: str
    province_code: str
    region: str


class Indicator(BaseModel):
    indicator_name: str
    unit: str
    indicator_category: str
    description: str


class Headline(BaseModel):
    reference_date: date
    geography: str
    employment: float | None
    unemployment: float | None
    unemployment_rate: float | None
    employment_rate: float | None
    participation_rate: float | None
    monthly_employment_change: float | None
    yoy_employment_change: float | None
    yoy_employment_change_pct: float | None
    unemployment_rate_change_mom: float | None
    unemployment_rate_change_yoy: float | None
    source_loaded_at: datetime


class PipelineRun(BaseModel):
    pipeline_run_id: UUID
    source_name: str
    started_at: datetime
    completed_at: datetime | None
    status: Literal["RUNNING", "SUCCESS", "FAILED", "PARTIAL"]
    records_extracted: int
    records_loaded: int
    records_rejected: int
    duration_seconds: float | None
    records_inserted: int | None = None
    records_updated: int | None = None
    records_unchanged: int | None = None
    latest_reference_date: date | None = None


class QualityResult(BaseModel):
    check_name: str
    table_name: str
    status: str
    observed_value: Any
    expected_condition: str
    checked_at: datetime


class SourceStatus(BaseModel):
    source: str
    status: str
    last_run: datetime | None = None
    last_successful_run: datetime | None = None
    records_processed: int | None = None
    duration_seconds: float | None = None
    latest_reference_date: date | None = None


class PipelineStatus(BaseModel):
    status: str
    last_run: datetime | None = None
    last_successful_refresh: datetime | None = None
    sources: list[SourceStatus]
    quality_checks: int
    quality_failures: int
    quality_results: list[QualityResult]


class Health(BaseModel):
    status: str
    database: str
    version: str
    last_pipeline_run: datetime | None = None
    last_successful_refresh: datetime | None = None


class Summary(BaseModel):
    labour: Headline | None
    interest_rate: InterestObservation | None
    warehouse_refreshed_at: datetime | None
    sources: list[str] = Field(default_factory=lambda: ["Statistics Canada", "Bank of Canada"])
