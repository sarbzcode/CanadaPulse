select 'labour' as source where
(select count(*) from {{ ref('fact_labour_market') }}) <>
(select count(*) from {{ source('raw', 'statcan_labour_force') }} where statistics = 'Estimate')
union all select 'rates' where
(select count(*) from {{ ref('fact_interest_rates') }}) <>
(select count(*) from {{ source('raw', 'bank_of_canada_observations') }})
