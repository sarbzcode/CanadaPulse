{{ config(indexes=[{'columns': ['series_key'], 'unique': true}]) }}
select distinct series_key, series_code, series_name, 'Percent'::text as unit, source
from {{ ref('int_interest_rate_observations') }}
