select
  order_date,
  channel,
  sum(amount) as revenue,
  count(*) as orders
from {{ ref('stg_orders') }}
group by 1, 2
