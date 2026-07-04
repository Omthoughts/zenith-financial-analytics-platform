with macro_data as (

    select *
    from {{ ref('stg_macro_indicators') }}

),

macro_changes as (

    select
        series_id,
        indicator_name,
        date,
        value,

        lag(value) over (
            partition by indicator_name
            order by date
        ) as previous_value,

        -- Absolute change from previous period
        round(
            value -
            lag(value) over (
                partition by indicator_name
                order by date
            ),
            4
        ) as absolute_change,

        -- Percentage change from previous period
        round(
            (
                value -
                lag(value) over (
                    partition by indicator_name
                    order by date
                )
            )
            /
            nullif(
                lag(value) over (
                    partition by indicator_name
                    order by date
                ),
                0
            )
            * 100,
            4
        ) as pct_change,

        -- 3-period rolling average (smoothed trend)
        round(
            avg(value) over (
                partition by indicator_name
                order by date
                rows between 2 preceding and current row
            ),
            4
        ) as rolling_3p_avg,

        -- 6-period rolling average (longer trend)
        round(
            avg(value) over (
                partition by indicator_name
                order by date
                rows between 5 preceding and current row
            ),
            4
        ) as rolling_6p_avg,

        -- Rank latest value per indicator (1 = most recent)
        row_number() over (
            partition by indicator_name
            order by date desc
        ) as recency_rank

    from macro_data

),

trend_signals as (

    select
        *,

        -- Trend direction based on absolute change
        case
            when absolute_change > 0 then 'INCREASING'
            when absolute_change < 0 then 'DECREASING'
            when absolute_change = 0 then 'STABLE'
            else 'UNKNOWN'
        end as trend_direction,

        -- Economic health signal per indicator
        -- CPI/Inflation: increasing = deteriorating (higher inflation = bad)
        -- Fed Funds Rate: context-dependent, flagged as neutral
        -- Unemployment: decreasing = improving (lower unemployment = good)
        -- GDP: increasing = improving
        case
            when indicator_name = 'inflation_cpi' and absolute_change > 0
                then 'DETERIORATING'
            when indicator_name = 'inflation_cpi' and absolute_change <= 0
                then 'IMPROVING'
            when indicator_name = 'unemployment_rate' and absolute_change > 0
                then 'DETERIORATING'
            when indicator_name = 'unemployment_rate' and absolute_change <= 0
                then 'IMPROVING'
            when indicator_name = 'gdp' and absolute_change > 0
                then 'IMPROVING'
            when indicator_name = 'gdp' and absolute_change <= 0
                then 'DETERIORATING'
            when indicator_name = 'fed_funds_rate'
                then 'NEUTRAL'
            else 'UNKNOWN'
        end as economic_health_signal

    from macro_changes

)

select *
from trend_signals
