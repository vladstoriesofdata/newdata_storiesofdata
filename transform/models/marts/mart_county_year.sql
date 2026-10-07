select
    county,
    fiscal_year,
    count(*) as companies,
    sum(turnover_ron) as turnover_ron,
    sum(profit_ron) as profit_ron,
    sum(employees) as employees,
    sum(fixed_assets_ron) as fixed_assets_ron,
    sum(current_assets_ron) as current_assets_ron,
    sum(liabilities_ron) as liabilities_ron,
    sum(equity_ron) as equity_ron,
    count(equity_ron) as companies_with_equity,
    sum(profit_ron) / nullif(sum(turnover_ron), 0) as profit_margin
from {{ ref('mart_company_year') }}
group by county, fiscal_year
