with portfolio as (


select *
from {{ ref('mart_portfolio_performance') }}


),

risk as (


select *
from {{ ref('mart_risk_metrics') }}


),

macro as (


select *
from {{ ref('mart_macro_summary') }}


),

macro_pivot as (


select
    max(case when indicator_name = 'inflation_cpi' then latest_value end) as inflation_cpi,
    max(case when indicator_name = 'fed_funds_rate' then latest_value end) as fed_funds_rate,
    max(case when indicator_name = 'unemployment_rate' then latest_value end) as unemployment_rate,
    max(case when indicator_name = 'gdp' then latest_value end) as gdp
from macro


)

select
p.symbol,
p.trading_days,
p.avg_daily_return_pct,
p.best_daily_return_pct,
p.worst_daily_return_pct,
r.volatility,
m.inflation_cpi,
m.fed_funds_rate,
m.unemployment_rate,
m.gdp

from portfolio p
left join risk r
on p.symbol = r.symbol

cross join macro_pivot m
