with equity_prices as (

    select *
    from {{ ref('stg_equity_prices') }}

),

returns_calculated as (

    select
        symbol,
        date,
        open,
        high,
        low,
        close,
        volume,

        lag(close) over (
            partition by symbol
            order by date
        ) as previous_close,

        round(
            (
                close -
                lag(close) over (
                    partition by symbol
                    order by date
                )
            )
            /
            nullif(
                lag(close) over (
                    partition by symbol
                    order by date
                ),
                0
            )
            * 100,
            4
        ) as daily_return_pct

    from equity_prices

),

rolling_metrics as (

    select
        symbol,
        date,
        open,
        high,
        low,
        close,
        volume,
        previous_close,
        daily_return_pct,

        -- 7-day rolling average return
        round(
            avg(daily_return_pct) over (
                partition by symbol
                order by date
                rows between 6 preceding and current row
            ),
            4
        ) as rolling_7d_avg_return_pct,

        -- 30-day rolling average return
        round(
            avg(daily_return_pct) over (
                partition by symbol
                order by date
                rows between 29 preceding and current row
            ),
            4
        ) as rolling_30d_avg_return_pct,

        -- 30-day rolling volatility (standard deviation of daily returns)
        round(
            stddev(daily_return_pct) over (
                partition by symbol
                order by date
                rows between 29 preceding and current row
            ),
            4
        ) as rolling_30d_volatility,

        -- 7-day rolling high (price range context)
        round(
            max(high) over (
                partition by symbol
                order by date
                rows between 6 preceding and current row
            ),
            4
        ) as rolling_7d_high,

        -- 7-day rolling low
        round(
            min(low) over (
                partition by symbol
                order by date
                rows between 6 preceding and current row
            ),
            4
        ) as rolling_7d_low,

        -- 30-day rolling average volume
        round(
            avg(volume) over (
                partition by symbol
                order by date
                rows between 29 preceding and current row
            ),
            0
        ) as rolling_30d_avg_volume,

        -- Cumulative return from first available date per symbol
        round(
            (
                close -
                first_value(close) over (
                    partition by symbol
                    order by date
                    rows between unbounded preceding and current row
                )
            )
            /
            nullif(
                first_value(close) over (
                    partition by symbol
                    order by date
                    rows between unbounded preceding and current row
                ),
                0
            )
            * 100,
            4
        ) as cumulative_return_pct,

        -- Row number for filtering (useful in marts)
        row_number() over (
            partition by symbol
            order by date desc
        ) as recency_rank

    from returns_calculated

)

select *
from rolling_metrics
