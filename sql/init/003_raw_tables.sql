create table if not exists raw.statcan_labour_force (
    raw_id bigserial primary key,
    reference_date date,
    reference_period text not null,
    geography text,
    dguid text,
    labour_force_characteristic text,
    sex text,
    age_group text,
    statistics text,
    value numeric,
    unit text,
    scalar_factor text,
    vector text,
    coordinate text,
    status text,
    symbol text,
    terminated text,
    decimals integer,
    source_table text not null,
    source text not null,
    source_file text,
    source_row_hash text not null unique,
    raw_payload jsonb not null,
    loaded_at timestamptz not null default now(),
    pipeline_run_id uuid references metadata.pipeline_runs (pipeline_run_id)
);

create index if not exists idx_statcan_labour_reference_date
    on raw.statcan_labour_force (reference_date);

create index if not exists idx_statcan_labour_geography
    on raw.statcan_labour_force (geography);

create index if not exists idx_statcan_labour_vector_date
    on raw.statcan_labour_force (vector, reference_date);

create table if not exists raw.bank_of_canada_observations (
    raw_id bigserial primary key,
    observation_date date not null,
    series_code text not null,
    series_name text not null,
    value numeric not null,
    source text not null,
    raw_payload jsonb not null,
    loaded_at timestamptz not null default now(),
    pipeline_run_id uuid references metadata.pipeline_runs (pipeline_run_id),
    constraint uq_boc_observation unique (observation_date, series_code)
);

create index if not exists idx_boc_observations_series_date
    on raw.bank_of_canada_observations (series_code, observation_date desc);

