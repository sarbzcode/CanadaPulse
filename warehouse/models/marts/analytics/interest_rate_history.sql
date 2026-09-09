{{ config(indexes=[{'columns': ['series_code', 'date'], 'unique': true}]) }}
select d.date, f.series_code, s.series_name, f.rate, f.loaded_at, f.pipeline_run_id
from {{ ref('fact_interest_rates') }} f
join {{ ref('dim_date') }} d using (date_key)
join {{ ref('dim_series') }} s using (series_key)
