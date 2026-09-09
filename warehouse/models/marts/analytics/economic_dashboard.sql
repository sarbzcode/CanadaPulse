select l.*, r.rate as overnight_rate, r.date as rate_observation_date,
    (l.reference_date < date_trunc('month', current_date)::date) as is_completed_month
from {{ ref('canada_labour_trends') }} l
left join lateral (
    select rate, date from {{ ref('interest_rate_history') }}
    where series_code = 'V39079' and date >= l.reference_date
        and date < l.reference_date + interval '1 month'
    order by date desc limit 1
) r on true
