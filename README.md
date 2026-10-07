# New Data

A single-machine analytics stack for mid-market clients: manufacturing, services, retail, e-commerce. Working size is up to about 100GB per client. MotherDuck calls this small data: it fits on one workstation, and a typical query touches a slice of it. The modeling can still be detailed. Governance is out of scope until a client asks for a catalog.

## Storage

One DuckDB file per client: `warehouse/analytics.duckdb`. Raw CSV, Parquet, and Excel files land in `0_data_sources/`. DuckDB reads them in place and spills to disk, so 100GB does not need a cluster or a second database. `firme_romania.xlsx` has two sheets. `date_financiare` is the yearly statement and `info_companii` is the company record. They join on `cui`. The pipeline loads each sheet into its own raw table.

## Processing

`python pipeline/run.py` loads raw files into a `raw` schema, then runs dbt seed, run, and test. Models live in `transform/`. The sample seed is a stand-in until a client file shows up. Polars is in the environment for files that are awkward in SQL. dlt is there for the first real source connector. Schedule the script with Task Scheduler when a refresh needs to run unattended.

## Semantic layer

`semantic/metrics.yml` names each measure. The SQL file next to it is the only definition dashboards may use. National and county pages read sums by year. The company page reads one CUI at a time.

## Visualization

Two code-built options, same semantic queries:

- `viz/` is an [Observable Framework](https://observablehq.com/framework/) app. A page is a Markdown file in git. Charts are [Observable Plot](https://observablehq.com/plot/) or D3 (`import * as d3 from "npm:d3"`). The data loader runs the semantic SQL and hands the page JSON. The 100GB file stays on disk.
- `viz/preview/index.html` is one HTML file and D3, for a deliverable that should not carry a framework.

Add a third page style, a small Vite app with live filter queries, only when a client needs to slice the full file interactively. Until then, pre-aggregated extracts are the page contract.

## Run

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python pipeline/run.py
cd viz
npm install
npm run dev
```

dbt is pinned to 1.8 because the 1.10 Windows parser extension does not load on the Python 3.9 install on this machine.

The bare D3 page reads a local JSON file, so open it through a local server after the pipeline has written the extract:

```powershell
cd viz\preview
python -m http.server 8765
```

Then open http://127.0.0.1:8765 .
