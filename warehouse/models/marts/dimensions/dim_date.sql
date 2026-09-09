{{ config(indexes=[{'columns': ['date_key'], 'unique': true}]) }}
with dates as (
    select reference_date as date from {{ ref('int_labour_observations') }}
    union all select observation_date from {{ ref('int_interest_rate_observations') }}
), bounds as (select min(date) as lo, max(date) as hi from dates), spine as (
    select generate_series(lo, hi, interval '1 day')::date as date from bounds
)
select to_char(date, 'YYYYMMDD')::integer as date_key, date,
    extract(year from date)::integer as year,
    extract(quarter from date)::integer as quarter,
    extract(month from date)::integer as month,
    trim(to_char(date, 'Month')) as month_name,
    to_char(date, 'YYYY-MM') as year_month,
    to_char(date, 'Mon YYYY') as year_month_label,
    (date = date_trunc('month', date)::date) as is_month_start,
    (date = (date_trunc('month', date) + interval '1 month - 1 day')::date) as is_month_end
from spine
