select date_key, geography_key, indicator_key, gender, age_group, adjustment, statistical_measure
from {{ ref('fact_labour_market') }}
group by 1,2,3,4,5,6,7 having count(*) > 1
