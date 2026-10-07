"""Load raw files, build dbt models, and refresh the preview extract."""

import re
import subprocess
import sys
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "0_data_sources"
WAREHOUSE = ROOT / "warehouse"
DB_PATH = WAREHOUSE / "analytics.duckdb"
TRANSFORM = ROOT / "transform"
PREVIEW = ROOT / "viz" / "preview" / "daily_revenue.json"


def table_name(path):
    name = re.sub(r"[^0-9A-Za-z_]", "_", path.stem).lower()
    if not name or name[0].isdigit():
        name = "t_" + name
    return name


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
            elif suffix == ".parquet":
                connection.execute(
                    "create or replace table raw.%s as select * from read_parquet(?)" % name,
                    [str(path)],
                )
            elif suffix == ".xlsx":
                connection.execute("install excel")
                connection.execute("load excel")
                connection.execute(
                    "create or replace table raw.%s as select * from read_xlsx(?, header = true)" % name,
                    [str(path)],
                )
            else:
                continue
            loaded.append("raw.%s" % name)
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
    import json

    PREVIEW.parent.mkdir(parents=True, exist_ok=True)
    PREVIEW.write_text(json.dumps(fetch_metric("daily_revenue"), indent=2) + "\n", encoding="utf-8")


def main():
    loaded = load_raw_files()
    if loaded:
        print("Loaded %s" % ", ".join(loaded))
    else:
        print("No CSV or Parquet files in 0_data_sources. Building the sample seed.")
    run_dbt("seed")
    run_dbt("run")
    run_dbt("test")
    write_preview()
    print("Warehouse: %s" % DB_PATH)
    print("Preview extract: %s" % PREVIEW)


if __name__ == "__main__":
    main()
