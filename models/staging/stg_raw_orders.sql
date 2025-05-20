{{
  config(
    materialized='view',
  )
}}

select
    order_id,
    user_id,
    cast(order_date as date) as order_date,
    status,
    amount
from {{ ref('raw_orders_seed') }} -- if using seed, or source('your_source_schema', 'raw_orders_table')