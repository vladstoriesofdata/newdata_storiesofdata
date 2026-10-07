with source as (
    select
        cast("CUI" as bigint) as cui,
        cast("Year" as integer) as fiscal_year,
        cast("Cifra" as double) as turnover_ron,
        cast("Profit" as double) as profit_ron,
        cast(round("Angajati") as integer) as employees,
        cast("ActiveImobilizate" as double) as fixed_assets_ron,
        cast("ActiveCirculante" as double) as current_assets_ron,
        cast("Stocuri" as double) as inventories_ron,
        cast("Disponibilitati" as double) as cash_ron,
        cast("Creante" as double) as receivables_ron,
        cast("Provizioane" as double) as provisions_ron,
        cast("Datorii" as double) as liabilities_ron,
        cast("Venituri" as double) as total_income_ron,
        cast("Cheltuieli" as double) as total_expenses_ron,
        cast("Capitaluri proprii" as double) as equity_ron
    from {{ source('raw', 'date_financiare') }}
),

-- Three companies are stored twice for 2021-2025. The copies match on
-- turnover and profit, so one row is kept.
ranked as (
    select
        *,
        row_number() over (partition by cui, fiscal_year order by cui) as row_number
    from source
)

select
    cui,
    fiscal_year,
    turnover_ron,
    profit_ron,
    employees,
    fixed_assets_ron,
    current_assets_ron,
    inventories_ron,
    cash_ron,
    receivables_ron,
    provisions_ron,
    liabilities_ron,
    total_income_ron,
    total_expenses_ron,
    equity_ron
from ranked
where row_number = 1
