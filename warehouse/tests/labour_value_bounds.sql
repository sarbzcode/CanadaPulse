select observation_key from {{ ref('fact_labour_market') }}
where value < 0 or (unit = 'Percent' and value > 100)
