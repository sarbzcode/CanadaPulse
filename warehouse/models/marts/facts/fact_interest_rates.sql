{{ config(indexes=[{'columns': ['observation_key'], 'unique': true},
    {'columns': ['series_key', 'date_key'], 'unique': true}]) }}
select observation_key, date_key, series_key, series_code, rate, source, loaded_at, pipeline_run_id
from {{ ref('int_interest_rate_observations') }}
