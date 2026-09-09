select
    source_row_hash as observation_key,
    reference_date::date as reference_date,
    trim(reference_period) as reference_period,
    trim(geography) as geography,
    nullif(trim(dguid), '') as dguid,
    trim(labour_force_characteristic) as indicator,
    trim(sex) as gender,
    trim(age_group) as age_group,
    trim(statistics) as statistical_measure,
    trim(data_type) as adjustment,
    value::numeric as value,
    trim(unit) as unit,
    trim(scalar_factor) as scalar_factor,
    nullif(trim(status), '') as source_status,
    vector, coordinate, source_table, source, source_file,
    loaded_at, pipeline_run_id
from {{ source('raw', 'statcan_labour_force') }}
