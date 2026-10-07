import sys
from pathlib import Path

import duckdb

XLSX = Path(sys.argv[1])
out = Path(__file__).with_name("_diagnose2.txt")
connection = duckdb.connect()
connection.execute("install excel")
connection.execute("load excel")
connection.execute(
    "create table fin as select * from read_xlsx(?, header = true, sheet = 'date_financiare')",
    [str(XLSX)],
)
connection.execute(
    "create table info as select * from read_xlsx(?, header = true, sheet = 'info_companii')",
    [str(XLSX)],
)

lines = []

def show(title, sql):
    lines.append("\n== " + title)
    cursor = connection.execute(sql)
    lines.append(" | ".join(d[0] for d in cursor.description))
    for row in cursor.fetchall():
        lines.append(repr(row))

show("jud_repr", "select Jud, count(*) as n from info group by 1 order by 2 desc")
show("flag", "select Flag, count(*) as n from info group by 1 order by 2 desc")
show("caen", "select CAEN, count(*) as n from info group by 1 order by 2 desc")
show(
    "dups",
    """
    select f.CUI::bigint as cui, i.Nume, f.Year::int as year, count(*) as n,
           count(distinct f.Cifra) as cifras, count(distinct f.Profit) as profits,
           min(f.Cifra) as min_cifra, max(f.Cifra) as max_cifra
    from fin f
    left join info i on f.CUI::bigint = i.cui::bigint
    group by 1, 2, 3
    having count(*) > 1
    order by 1, 3
    """,
)
show(
    "brands",
    """
    select i.Brand, i.Nume, f.Year::int as year, f.Cifra, f.Profit, f.Angajati
    from fin f
    join info i on f.CUI::bigint = i.cui::bigint
    where i.Brand in ('McDonald''s', 'KFC') and f.Year::int in (2023, 2024, 2025)
    order by i.Brand, f.Year
    """,
)
show(
    "info_only",
    """
    select i.cui::bigint, i.Nume, i.Jud, i.Brand
    from info i
    anti join fin f on i.cui::bigint = f.CUI::bigint
    """,
)

out.write_text("\n".join(lines), encoding="utf-8")
print("wrote", out, "lines", len(lines))
