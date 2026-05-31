select
*
from {{ source('zenith_raw', 'raw_equity_prices') }}
