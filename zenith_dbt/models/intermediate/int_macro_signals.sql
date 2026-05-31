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

        round(
            (
                value -
                lag(value) over (
                    partition by indicator_name
                    order by date
                )
            ),
            4
        ) as absolute_change

    from macro_data

)

select *
from macro_changes