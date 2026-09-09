alter table metadata.pipeline_runs add column if not exists records_inserted bigint;
alter table metadata.pipeline_runs add column if not exists records_updated bigint;
alter table metadata.pipeline_runs add column if not exists records_unchanged bigint;
alter table metadata.pipeline_runs add column if not exists latest_reference_date date;

create table if not exists metadata.data_quality_results (
    result_id bigserial primary key,
    pipeline_run_id uuid not null references metadata.pipeline_runs(pipeline_run_id),
    check_name text not null,
    table_name text not null,
    status text not null check (status in ('PASS', 'WARN', 'FAIL')),
    observed_value jsonb not null,
    expected_condition text not null,
    checked_at timestamptz not null default now()
);
create index if not exists idx_quality_run
    on metadata.data_quality_results(pipeline_run_id, checked_at desc);
