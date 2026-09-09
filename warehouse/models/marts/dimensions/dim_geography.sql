{{ config(indexes=[{'columns': ['geography_key'], 'unique': true}]) }}
with observed as (
    select distinct geography_key, geography from {{ ref('int_labour_observations') }}
)
select o.geography_key, o.geography as geography_name,
    m.geography_type, m.province_code, m.region, m.country
from observed o left join {{ ref('geography_metadata') }} m on o.geography = m.geography_name
