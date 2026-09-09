alter table raw.statcan_labour_force add column if not exists data_type text;

create or replace view analytics.labour_market as
select reference_date as date, geography, labour_force_characteristic as indicator,
       sex as gender, age_group, statistics, data_type as adjustment,
       value, unit, scalar_factor, status as source_status, vector,
       loaded_at, pipeline_run_id
from raw.statcan_labour_force
where statistics = 'Estimate';

create or replace view analytics.interest_rates as
select observation_date as date, series_code, series_name, value as rate,
       loaded_at, pipeline_run_id
from raw.bank_of_canada_observations;

create index if not exists idx_labour_dashboard
on raw.statcan_labour_force
(geography, labour_force_characteristic, sex, age_group, data_type, reference_date);
