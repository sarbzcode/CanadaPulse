select reference_date, geography from {{ ref('province_labour_summary') }}
group by 1,2 having count(*) > 1
