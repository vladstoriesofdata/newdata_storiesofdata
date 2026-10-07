import {execFileSync} from "node:child_process";
import {dirname, join} from "node:path";
import {fileURLToPath} from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const root = join(here, "..", "..", "..");
const python = join(root, ".venv", "Scripts", "python.exe");
const exporter = join(root, "pipeline", "export_metric.py");

process.stdout.write(execFileSync(python, [exporter, "county_year"], {maxBuffer: 64 * 1024 * 1024}));
