{{ config(indexes=[{'columns': ['geography', 'reference_date'], 'unique': true}]) }}
with pivoted as (
    select date as reference_date, geography, geography_type,
        max(value_base_units) filter (where indicator = 'Employment') as employment,
        max(value_base_units) filter (where indicator = 'Unemployment') as unemployment,
        max(value) filter (where indicator = 'Unemployment rate') as unemployment_rate,
        max(value) filter (where indicator = 'Employment rate') as employment_rate,
        max(value) filter (where indicator = 'Participation rate') as participation_rate,
        max(loaded_at) as source_loaded_at
    from {{ ref('labour_observations') }}
    where gender = 'Total - Gender' and age_group = '15 years and over'
      and adjustment = 'Seasonally adjusted'
    group by 1, 2, 3
), lagged as (
    select *, lag(reference_date) over w as previous_date,
        lag(employment) over w as previous_employment,
        lag(unemployment_rate) over w as previous_unemployment_rate
    from pivoted window w as (partition by geography order by reference_date)
)
select a.reference_date, a.geography, a.geography_type, a.employment, a.unemployment,
    a.unemployment_rate, a.employment_rate, a.participation_rate, a.source_loaded_at,
    case when a.previous_date = (a.reference_date - interval '1 month')::date
        then a.employment - a.previous_employment end as monthly_employment_change,
    a.employment - y.employment as yoy_employment_change,
    100.0 * (a.employment - y.employment) / nullif(y.employment, 0) as yoy_employment_change_pct,
    case when a.previous_date = (a.reference_date - interval '1 month')::date
        then a.unemployment_rate - a.previous_unemployment_rate end as unemployment_rate_change_mom,
    a.unemployment_rate - y.unemployment_rate as unemployment_rate_change_yoy
from lagged a left join pivoted y on a.geography = y.geography
    and y.reference_date = (a.reference_date - interval '1 year')::date
