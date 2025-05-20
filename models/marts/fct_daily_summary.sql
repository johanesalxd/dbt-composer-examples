{{
  config(
    materialized='incremental',
  )
}}

select
    order_date,
    count(distinct order_id) as number_of_orders,
    sum(case when status = 'completed' then 1 else 0 end) as completed_orders,
    sum(amount) as total_amount
from {{ ref('stg_raw_orders') }}
group by 1

{% if is_incremental() %}

  where order_date >= (select max(order_date) from {{ this }})

{% endif %}
