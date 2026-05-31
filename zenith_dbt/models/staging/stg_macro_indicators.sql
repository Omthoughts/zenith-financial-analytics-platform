select
*
from {{ source('zenith_raw', 'raw_macro_indicators') }}
