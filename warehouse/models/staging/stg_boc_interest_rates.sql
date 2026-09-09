select
    {{ stable_key(['observation_date', 'series_code']) }} as observation_key,
    observation_date::date as observation_date,
    upper(trim(series_code)) as series_code,
    trim(series_name) as series_name,
    value::numeric as rate,
    source, loaded_at, pipeline_run_id
from {{ source('raw', 'bank_of_canada_observations') }}
