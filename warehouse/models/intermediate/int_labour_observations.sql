select *,
    {{ stable_key(['geography']) }} as geography_key,
    {{ stable_key(['indicator', 'unit', 'scalar_factor']) }} as indicator_key,
    to_char(reference_date, 'YYYYMMDD')::integer as date_key,
    case scalar_factor when 'thousands' then value * 1000
         when 'units' then value end as value_base_units,
    (value is null) as is_missing
from {{ ref('stg_statcan_labour') }}
where statistical_measure = 'Estimate'
