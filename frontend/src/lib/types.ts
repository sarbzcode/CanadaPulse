export type Labour = {
  date: string;
  geography: string;
  indicator: string;
  gender: string;
  age_group: string;
  adjustment: string;
  value: number | null;
  unit: string;
  scalar_factor: string;
  source_status: string | null;
  loaded_at: string;
};
export type Rate = {
  date: string;
  series_code: string;
  series_name: string;
  rate: number;
  loaded_at: string;
};
export type Headline = {
  reference_date: string;
  geography: string;
  employment: number | null;
  unemployment: number | null;
  unemployment_rate: number | null;
  employment_rate: number | null;
  participation_rate: number | null;
  monthly_employment_change: number | null;
  yoy_employment_change: number | null;
  yoy_employment_change_pct: number | null;
  unemployment_rate_change_mom: number | null;
  unemployment_rate_change_yoy: number | null;
  source_loaded_at: string;
};
export type Summary = {
  labour: Headline | null;
  interest_rate: Rate | null;
  warehouse_refreshed_at: string | null;
  sources: string[];
};
export type Filters = {
  geography: string[];
  indicator: string[];
  gender: string[];
  age_group: string[];
  adjustment: string[];
};
export type Run = {
  pipeline_run_id: string;
  source_name: string;
  started_at: string;
  completed_at: string | null;
  status: string;
  records_extracted: number;
  records_loaded: number;
  records_rejected: number;
  duration_seconds: number | null;
  records_inserted: number | null;
  records_updated: number | null;
  records_unchanged: number | null;
  latest_reference_date: string | null;
};
export type Pipeline = {
  status: string;
  last_run: string | null;
  last_successful_refresh: string | null;
  quality_checks: number;
  quality_failures: number;
  sources: {
    source: string;
    status: string;
    last_successful_run: string | null;
    records_processed: number | null;
    duration_seconds: number | null;
    latest_reference_date: string | null;
  }[];
  quality_results: {
    check_name: string;
    table_name: string;
    status: string;
    observed_value: unknown;
    expected_condition: string;
    checked_at: string;
  }[];
};
