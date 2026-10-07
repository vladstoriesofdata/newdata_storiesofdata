select
    cui,
    fiscal_year,
    company_name,
    brand,
    county,
    turnover_ron,
    profit_ron,
    employees,
    fixed_assets_ron,
    current_assets_ron,
    liabilities_ron,
    equity_ron,
    inventories_ron,
    cash_ron,
    receivables_ron,
    provisions_ron,
    total_income_ron,
    total_expenses_ron,
    profit_margin
from marts.mart_company_year
order by company_name, fiscal_year
