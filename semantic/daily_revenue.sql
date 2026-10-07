select
  order_date::varchar as order_date,
  channel,
  revenue,
  orders
from marts.daily_revenue
order by 1, 2
