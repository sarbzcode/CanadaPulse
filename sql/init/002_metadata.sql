create table if not exists metadata.pipeline_runs (
    pipeline_run_id uuid primary key,
    pipeline_name text not null,
    source_name text not null,
    started_at timestamptz not null,
    completed_at timestamptz,
    status text not null check (status in ('RUNNING', 'SUCCESS', 'FAILED', 'PARTIAL')),
    records_extracted bigint not null default 0 check (records_extracted >= 0),
    records_loaded bigint not null default 0 check (records_loaded >= 0),
    records_rejected bigint not null default 0 check (records_rejected >= 0),
    duration_seconds numeric(14, 3),
    error_message text,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    constraint completed_runs_have_completed_at
        check (status = 'RUNNING' or completed_at is not null)
);

create index if not exists idx_pipeline_runs_source_started_at
    on metadata.pipeline_runs (source_name, started_at desc);

create index if not exists idx_pipeline_runs_status
    on metadata.pipeline_runs (status);

