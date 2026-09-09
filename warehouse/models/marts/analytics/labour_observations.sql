{{ config(indexes=[{'columns': ['geography', 'indicator', 'gender', 'age_group', 'adjustment', 'date']},
    {'columns': ['date', 'indicator', 'gender', 'age_group', 'adjustment']}]) }}
select f.observation_key, d.date, g.geography_name as geography,
    g.geography_type, i.indicator_name as indicator,
    f.gender, f.age_group, f.adjustment, f.statistical_measure as statistics,
    f.value, f.value_base_units, f.unit, f.scalar_factor, f.source_status,
    f.vector, f.coordinate, f.source_table, f.loaded_at, f.pipeline_run_id
from {{ ref('fact_labour_market') }} f
join {{ ref('dim_date') }} d using (date_key)
join {{ ref('dim_geography') }} g using (geography_key)
join {{ ref('dim_indicator') }} i using (indicator_key)
