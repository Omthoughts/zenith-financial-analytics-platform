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
            lag(close) over (
                partition by symbol
                order by date
            )
            * 100,
            4
        ) as daily_return_pct

    from equity_prices

)

select *
from returns_calculated