select * from {{ ref('province_labour_summary') }} where geography = 'Canada'
