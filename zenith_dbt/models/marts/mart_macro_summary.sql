with latest_macro as (

select
    indicator_name,
    value,
    date,
    row_number() over (
        partition by indicator_name
        order by date desc
    ) as rn

from {{ ref('int_macro_signals') }}


)

select
indicator_name,
value as latest_value,
date as latest_date

from latest_macro

where rn = 1
