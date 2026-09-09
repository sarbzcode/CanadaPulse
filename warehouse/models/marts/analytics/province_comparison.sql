select * from {{ ref('province_labour_summary') }}
where geography_type in ('province', 'territory')
