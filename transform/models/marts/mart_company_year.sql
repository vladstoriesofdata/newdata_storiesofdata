select
    financials.cui,
    financials.fiscal_year,
    companies.company_name,
    companies.brand,
    companies.county,
    companies.locality,
    companies.segment,
    companies.caen,
    companies.caen_label,
    financials.turnover_ron,
    financials.profit_ron,
    financials.employees,
    financials.fixed_assets_ron,
    financials.current_assets_ron,
    financials.liabilities_ron,
    financials.equity_ron,
    financials.inventories_ron,
    financials.cash_ron,
    financials.receivables_ron,
    financials.provisions_ron,
    financials.total_income_ron,
    financials.total_expenses_ron,
    financials.profit_ron / nullif(financials.turnover_ron, 0) as profit_margin
from {{ ref('stg_financials') }} as financials
left join {{ ref('stg_companies') }} as companies
    on financials.cui = companies.cui
