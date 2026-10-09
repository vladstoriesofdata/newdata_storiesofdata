with yearly as (
    select * from {{ ref('mart_national_year') }}
),

bounds as (
    select max(fiscal_year) as current_year
    from yearly
),

anchored as (
    select
        bounds.current_year,
        bounds.current_year - 3 as start_year_3,
        bounds.current_year - 10 as start_year_10,
        now.turnover_ron as turnover_now,
        y3.turnover_ron as turnover_3,
        y10.turnover_ron as turnover_10,
        now.profit_ron as profit_now,
        y3.profit_ron as profit_3,
        y10.profit_ron as profit_10,
        now.liabilities_ron as liabilities_now,
        y3.liabilities_ron as liabilities_3,
        y10.liabilities_ron as liabilities_10
    from bounds
    inner join yearly as now
        on now.fiscal_year = bounds.current_year
    inner join yearly as y3
        on y3.fiscal_year = bounds.current_year - 3
    inner join yearly as y10
        on y10.fiscal_year = bounds.current_year - 10
)

select
    current_year,
    start_year_3,
    start_year_10,
    case
        when turnover_3 > 0 and turnover_now > 0
            then power(turnover_now / turnover_3, 1.0 / 3) - 1
    end as turnover_cagr_3,
    case
        when turnover_10 > 0 and turnover_now > 0
            then power(turnover_now / turnover_10, 1.0 / 10) - 1
    end as turnover_cagr_10,
    case
        when profit_3 > 0 and profit_now > 0
            then power(profit_now / profit_3, 1.0 / 3) - 1
    end as profit_cagr_3,
    case
        when profit_10 > 0 and profit_now > 0
            then power(profit_now / profit_10, 1.0 / 10) - 1
    end as profit_cagr_10,
    case
        when liabilities_3 > 0 and liabilities_now > 0
            then power(liabilities_now / liabilities_3, 1.0 / 3) - 1
    end as liabilities_cagr_3,
    case
        when liabilities_10 > 0 and liabilities_now > 0
            then power(liabilities_now / liabilities_10, 1.0 / 10) - 1
    end as liabilities_cagr_10
from anchored
