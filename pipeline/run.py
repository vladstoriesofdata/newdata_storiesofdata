"""Load raw files, build dbt models, and refresh the preview extracts."""

import json
import re
import subprocess
import sys
import tempfile
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "0_data_sources"
WAREHOUSE = ROOT / "warehouse"
DB_PATH = WAREHOUSE / "analytics.duckdb"
TRANSFORM = ROOT / "transform"
PREVIEW_DIR = ROOT / "viz" / "preview"
METRICS = ("national_year", "county_year", "companies", "company_year")
MAIN_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"


def table_name(path):
    name = re.sub(r"[^0-9A-Za-z_]", "_", path.stem).lower()
    if not name or name[0].isdigit():
        name = "t_" + name
    return name


def xlsx_sheet_names(path):
    with zipfile.ZipFile(path) as book:
        root = ET.fromstring(book.read("xl/workbook.xml"))
    return [
        sheet.attrib["name"]
        for sheet in root.findall("{%s}sheets/{%s}sheet" % (MAIN_NS, MAIN_NS))
    ]


def copy_shared_read(src, dst):
    """Read a file that Excel may already have open. Never writes to src."""
    import ctypes

    generic_read = 0x80000000
    share = 0x1 | 0x2 | 0x4
    handle = ctypes.windll.kernel32.CreateFileW(
        str(src), generic_read, share, None, 3, 0x80, None
    )
    if handle == ctypes.c_void_p(-1).value:
        raise ctypes.WinError()
    try:
        with open(dst, "wb") as target:
            while True:
                chunk = ctypes.create_string_buffer(1024 * 1024)
                read = ctypes.c_ulong(0)
                ok = ctypes.windll.kernel32.ReadFile(
                    handle, chunk, len(chunk), ctypes.byref(read), None
                )
                if not ok:
                    raise ctypes.WinError()
                if read.value == 0:
                    break
                target.write(chunk.raw[: read.value])
    finally:
        ctypes.windll.kernel32.CloseHandle(handle)


def load_xlsx(connection, path):
    # DuckDB reads a temporary copy. The workbook in 0_data_sources is not modified.
    with tempfile.TemporaryDirectory() as temporary:
        local = Path(temporary) / path.name
        copy_shared_read(path, local)
        loaded = []
        for sheet in xlsx_sheet_names(local):
            name = table_name(Path(sheet))
            connection.execute(
                "create or replace table raw.%s as select * from read_xlsx(?, header = true, sheet = ?)"
                % name,
                [str(local), sheet],
            )
            loaded.append("raw.%s" % name)
        file_table = table_name(path)
        if file_table not in [table.split(".", 1)[1] for table in loaded]:
            connection.execute("drop table if exists raw.%s" % file_table)
        return loaded


def load_raw_files():
    WAREHOUSE.mkdir(parents=True, exist_ok=True)
    connection = duckdb.connect(str(DB_PATH))
    loaded = []
    try:
        connection.execute("create schema if not exists raw")
        for path in sorted(RAW.iterdir()):
            suffix = path.suffix.lower()
            name = table_name(path)
            if suffix == ".csv":
                connection.execute(
                    "create or replace table raw.%s as select * from read_csv_auto(?)" % name,
                    [str(path)],
                )
                loaded.append("raw.%s" % name)
            elif suffix == ".parquet":
                connection.execute(
                    "create or replace table raw.%s as select * from read_parquet(?)" % name,
                    [str(path)],
                )
                loaded.append("raw.%s" % name)
            elif suffix == ".xlsx":
                connection.execute("install excel")
                connection.execute("load excel")
                loaded.extend(load_xlsx(connection, path))
    finally:
        connection.close()
    return loaded


def dbt_bin():
    scripts = Path(sys.executable).parent
    for name in ("dbt.exe", "dbt"):
        candidate = scripts / name
        if candidate.exists():
            return str(candidate)
    return "dbt"


def run_dbt(command):
    subprocess.check_call(
        [dbt_bin(), command, "--profiles-dir", "."],
        cwd=str(TRANSFORM),
    )


def write_preview():
    sys.path.insert(0, str(ROOT))
    from pipeline.export_metric import fetch_metric

    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    for metric in METRICS:
        target = PREVIEW_DIR / (metric + ".json")
        rows = fetch_metric(metric)
        target.write_text(json.dumps(rows, ensure_ascii=False) + "\n", encoding="utf-8")
        print("Preview extract: %s (%s rows)" % (target, len(rows)))


def main():
    loaded = load_raw_files()
    if loaded:
        print("Loaded %s" % ", ".join(loaded))
    else:
        print("No source files in 0_data_sources. Building the sample seed.")
    run_dbt("seed")
    run_dbt("run")
    run_dbt("test")
    write_preview()
    print("Warehouse: %s" % DB_PATH)


if __name__ == "__main__":
    main()
