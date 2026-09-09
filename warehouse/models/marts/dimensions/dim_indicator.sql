{{ config(indexes=[{'columns': ['indicator_key'], 'unique': true}]) }}
select distinct indicator_key, indicator as indicator_name, unit, scalar_factor,
    case when unit = 'Percent' then 'Rate' else 'Population count' end as indicator_category,
    indicator || ' as published by Statistics Canada; source unit: ' || unit as description
from {{ ref('int_labour_observations') }}
