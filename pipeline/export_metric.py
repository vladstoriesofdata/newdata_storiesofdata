"""Print one semantic metric as JSON.

Usage: python pipeline/export_metric.py daily_revenue
"""

import json
import sys
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "warehouse" / "analytics.duckdb"


def json_ready(value):
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    return value


def fetch_metric(metric):
    sql_path = ROOT / "semantic" / (metric + ".sql")
    if not sql_path.exists():
        raise SystemExit("No semantic query at %s" % sql_path)
    if not DB_PATH.exists():
        raise SystemExit("No warehouse at %s. Run python pipeline/run.py first." % DB_PATH)

    connection = duckdb.connect(str(DB_PATH), read_only=True)
    try:
        cursor = connection.execute(sql_path.read_text(encoding="utf-8"))
        columns = [column[0] for column in cursor.description]
        return [
            {column: json_ready(value) for column, value in zip(columns, row)}
            for row in cursor.fetchall()
        ]
    finally:
        connection.close()


def main():
    metric = sys.argv[1] if len(sys.argv) > 1 else "daily_revenue"
    json.dump(fetch_metric(metric), sys.stdout)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
