select
    cui,
    fiscal_year,
    count(*) as row_count
from {{ ref('stg_financials') }}
group by cui, fiscal_year
having count(*) > 1
