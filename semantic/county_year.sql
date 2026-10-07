select
    county,
    fiscal_year,
    companies,
    turnover_ron,
    profit_ron,
    employees,
    fixed_assets_ron,
    current_assets_ron,
    liabilities_ron,
    equity_ron,
    companies_with_equity,
    profit_margin
from marts.mart_county_year
order by fiscal_year, turnover_ron desc
