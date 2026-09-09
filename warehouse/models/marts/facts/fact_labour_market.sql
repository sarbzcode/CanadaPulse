{{ config(indexes=[{'columns': ['observation_key'], 'unique': true},
    {'columns': ['geography_key', 'indicator_key', 'date_key']}]) }}
select observation_key, date_key, geography_key, indicator_key,
    gender, age_group, adjustment, statistical_measure,
    value, value_base_units, unit, scalar_factor, is_missing, source_status,
    vector, coordinate, source_table, source, source_file, loaded_at, pipeline_run_id
from {{ ref('int_labour_observations') }}
