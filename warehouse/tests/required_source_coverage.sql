-- Empty sources cannot produce a successfully published economic dashboard.
select 'labour' as missing_source
where not exists (select 1 from {{ source('raw', 'statcan_labour_force') }})
union all
select 'interest_rates'
where not exists (select 1 from {{ source('raw', 'bank_of_canada_observations') }})
