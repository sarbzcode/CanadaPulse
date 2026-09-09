select observation_key from {{ ref('stg_statcan_labour') }}
where reference_date <> date_trunc('month', reference_date)::date
