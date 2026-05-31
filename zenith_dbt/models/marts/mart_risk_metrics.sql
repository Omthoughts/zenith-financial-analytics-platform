select
symbol,

count(*) as observations,

round(avg(daily_return_pct), 4) as avg_return,

round(stddev(daily_return_pct), 4) as volatility,

round(min(daily_return_pct), 4) as max_loss,

round(max(daily_return_pct), 4) as max_gain

from {{ ref('int_equity_returns') }}

where daily_return_pct is not null

group by symbol