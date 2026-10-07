"""Check grains, join coverage, and accounting identities before modeling."""

import os
import sys
from pathlib import Path

import duckdb

XLSX = Path(sys.argv[1])
connection = duckdb.connect()
connection.execute("install excel")
connection.execute("load excel")
connection.execute(
    """
    create table fin as
    select * from read_xlsx(?, header = true, sheet = 'date_financiare')
    """,
    [str(XLSX)],
)
connection.execute(
    """
    create table info as
    select * from read_xlsx(?, header = true, sheet = 'info_companii')
    """,
    [str(XLSX)],
)

queries = {
    "years": """
        select Year::int as year, count(*) as rows, count(distinct CUI) as companies
        from fin group by 1 order by 1
    """,
    "dup_cui_year": """
        select count(*) from (
          select CUI, Year from fin group by 1, 2 having count(*) > 1
        )
    """,
    "cui_not_integer": """
        select count(*) from fin where CUI != floor(CUI)
        union all
        select count(*) from info where cui != floor(cui)
    """,
    "join": """
        select
          (select count(distinct CUI::bigint) from fin) as fin_cui,
          (select count(distinct cui::bigint) from info) as info_cui,
          (select count(*) from (select distinct CUI::bigint as cui from fin) f
            anti join (select distinct cui::bigint as cui from info) i using (cui)) as fin_only,
          (select count(*) from (select distinct cui::bigint as cui from info) i
            anti join (select distinct CUI::bigint as cui from fin) f using (cui)) as info_only
    """,
    "profit_vs_income": """
        select
          count(*) as rows_with_income,
          count(*) filter (where abs(Profit - (Venituri - Cheltuieli)) < 1) as profit_equals_income_minus_expense,
          count(*) filter (where abs(Profit - (Venituri - Cheltuieli)) >= 1) as profit_differs
        from fin
        where Venituri is not null and Cheltuieli is not null
    """,
    "sparse_by_year": """
        select Year::int as year,
          count(*) as rows,
          count(Stocuri) as stocuri,
          count(Venituri) as venituri,
          count(Provizioane) as provizioane
        from fin
        group by 1
        order by 1
    """,
    "current_assets_identity": """
        select
          count(*) as filled,
          count(*) filter (
            where abs(ActiveCirculante - (coalesce(Stocuri, 0) + coalesce(Disponibilitati, 0) + coalesce(Creante, 0))) < 1
          ) as matches
        from fin
        where Stocuri is not null or Disponibilitati is not null or Creante is not null
    """,
    "jud": "select Jud, count(*) as companies from info group by 1 order by 2 desc",
    "flag": "select Flag, count(*) from info group by 1 order by 2 desc",
    "caen": "select CAEN, count(*) from info group by 1 order by 2 desc",
    "mcdonalds": """
        select i.Nume, i.Brand, f.Year::int, f.Cifra, f.Profit, f.Angajati
        from fin f
        join info i on f.CUI::bigint = i.cui::bigint
        where i.Brand = 'McDonald''s'
        order by f.Year
    """,
    "margin_extremes": """
        select
          min(Cifra), max(Cifra),
          count(*) filter (where Cifra = 0) as zero_turnover,
          count(*) filter (where Cifra < 0) as negative_turnover
        from fin
    """,
}

for name, sql in queries.items():
    print("\n==", name)
    cursor = connection.execute(sql)
    cols = [d[0] for d in cursor.description]
    print(cols)
    for row in cursor.fetchall():
        print(row)
