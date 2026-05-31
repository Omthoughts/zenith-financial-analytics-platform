select
symbol,


count(*) as trading_days,

round(avg(daily_return_pct), 4) as avg_daily_return_pct,

round(min(daily_return_pct), 4) as worst_daily_return_pct,

round(max(daily_return_pct), 4) as best_daily_return_pct


from {{ ref('int_equity_returns') }}

where daily_return_pct is not null

group by symbol
