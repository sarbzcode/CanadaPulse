select *,
    to_char(observation_date, 'YYYYMMDD')::integer as date_key,
    {{ stable_key(['series_code']) }} as series_key
from {{ ref('stg_boc_interest_rates') }}
