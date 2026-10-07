"""Profile both sheets of the company workbook."""

import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

import duckdb

import sys

ROOT = Path(__file__).resolve().parents[1]
XLSX = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "0_data_sources" / "firme_romania.xlsx"
MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL = "http://schemas.openxmlformats.org/package/2006/relationships"
OFFICE_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"


def workbook_sheets():
    with zipfile.ZipFile(XLSX) as book:
        root = ET.fromstring(book.read("xl/workbook.xml"))
        rels = ET.fromstring(book.read("xl/_rels/workbook.xml.rels"))
    targets = {}
    for rel in rels:
        targets[rel.attrib["Id"]] = rel.attrib["Target"]
    sheets = []
    for sheet in root.findall(f"{{{MAIN}}}sheets/{{{MAIN}}}sheet"):
        rid = sheet.attrib[f"{{{OFFICE_REL}}}id"]
        sheets.append((sheet.attrib["name"], targets[rid]))
    return sheets


def profile(connection, label, relation_sql, params):
    print(f"\n===== {label} =====")
    cursor = connection.execute(f"select * from {relation_sql} limit 0", params)
    columns = [item[0] for item in cursor.description]
    connection.execute(
        f"create or replace temp table profiled as select * from {relation_sql}",
        params,
    )
    row_count = connection.execute("select count(*) from profiled").fetchone()[0]
    print("rows", row_count)
    print("columns", columns)
    for column in columns:
        quoted = '"' + column.replace('"', '""') + '"'
        nulls, distinct = connection.execute(
            f"select count(*) filter (where {quoted} is null), count(distinct {quoted}) from profiled"
        ).fetchone()
        sample = connection.execute(
            f"select {quoted} from profiled where {quoted} is not null limit 5"
        ).fetchall()
        print(f"  {column}: nulls={nulls} distinct={distinct} sample={[row[0] for row in sample]}")


def main():
    sheets = workbook_sheets()
    print("SHEETS", sheets)
    connection = duckdb.connect()
    connection.execute("install excel")
    connection.execute("load excel")
    for name, _target in sheets:
        profile(
            connection,
            name,
            "read_xlsx(?, header = true, sheet = ?)",
            [str(XLSX), name],
        )


if __name__ == "__main__":
    main()
