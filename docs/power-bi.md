# Power BI integration

Power BI is an optional analyst client; Next.js is the public frontend. No `.pbix` file is
claimed or fabricated. Connect Power BI Desktop to PostgreSQL using a reader login and
import the dbt models after a successful warehouse refresh.

## Recommended model

For flexible analysis import warehouse.dim_date, dim_geography, dim_indicator,
fact_labour_market, dim_series and fact_interest_rates. Use one-to-many, single-direction
relationships on the documented keys. Keep demographic and adjustment filters explicit.
For simpler report pages import analytics.province_labour_summary, canada_labour_trends,
province_comparison, economic_dashboard and interest_rate_history.

## Report pages

| Page | Models and visuals |
|---|---|
| Canada overview | canada_labour_trends; latest headline cards and monthly trends |
| Province comparison | province_comparison; one selected month, rate bars, geography slicer |
| Labour trends | fact_labour_market with dimensions; indicator, gender, age and adjustment slicers |
| Economic indicators | economic_dashboard and interest_rate_history; labelled monthly alignment or separate daily chart |
| Data freshness | safe API pipeline status or selected metadata fields, no error traces |

Employment fields in headline marts are persons. Fact values retain source units (often
thousands). Never sum percentages or add Canada to its provinces. Avoid mixing seasonal
adjustments. Rates use percentage-point changes; employment growth percentages use the
exact prior-year period. Missing values remain blank in visuals.

Recommended measures: current unemployment rate, employment MoM/YoY change, employment
growth YoY percent, participation rate, employment rate and overnight rate. Most calculations
are already tested in dbt. A measure returning a latest rate should require one geography:

```dax
Current Unemployment Rate =
IF (
    HASONEVALUE ( province_labour_summary[geography] ),
    VAR LatestPeriod = MAX ( province_labour_summary[reference_date] )
    RETURN CALCULATE (
        MAX ( province_labour_summary[unemployment_rate] ),
        province_labour_summary[reference_date] = LatestPeriod
    )
)
```

Configure refresh after the warehouse build, not during ingestion. Show source/reference dates
on every page. If a real report is created later, add its screenshots and model documentation.
