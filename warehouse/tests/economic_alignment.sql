select reference_date from {{ ref('economic_dashboard') }}
where rate_observation_date < reference_date
   or rate_observation_date >= reference_date + interval '1 month'
