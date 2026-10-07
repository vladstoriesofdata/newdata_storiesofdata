select
  order_id,
  cast(order_date as date) as order_date,
  channel,
  cast(amount as double) as amount
from {{ ref('orders') }}
