# cot_willco_index

`cot_willco_index` is a Flask + pandas project for analyzing CFTC Commitments of Traders (COT) legacy futures data and computing Williams Commercial Index-style signals.

## What the project does

- Loads (or builds) a local `cot.csv` dataset from CFTC legacy futures reports
- Computes trader-group net positioning metrics for:
  - Commercials
  - Large Speculators (Non-Commercials)
  - Small Speculators (Non-Reportables)
- Calculates Williams-style indexes (`0-100`) across these lookbacks:
  - 26 weeks (0.5y)
  - 52 weeks (1y)
  - 104 weeks (2y)
  - 156 weeks (3y)
  - 208 weeks (4y)
  - 260 weeks (5y)
- Serves a web UI with table filters for potential setups and per-asset views

## Repository structure

- `index.py`: Flask app entrypoint (routes, table generation, filtering, styling)
- `willco.py`: COT data fetch/prepare logic and WillCo calculations
- `templates/index.html`: Flask template for the table UI
- `.gitignore`: ignores generated artifacts such as `cot.csv`, `cot/`, and local envs
- `LICENSE`: GPL-3.0 license text

Common generated local artifacts:

- `cot.csv`: consolidated COT dataset used by the app
- `annual.txt`: large local data artifact
- `cot/`: per-market CSV exports from `generate_csvs.py`

## Requirements

- Python 3.10+
- `flask`
- `pandas`
- `cot-reports`

Example install (recommended on Debian/Ubuntu and other externally-managed Python installs):

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install flask pandas cot-reports
```

## Run the web app

From the repository root:

```bash
python index.py
```

Then open:

- `http://127.0.0.1:5000`

## Data bootstrap behavior

`WillCo` checks for `cot.csv` at startup.

- If `cot.csv` exists, it is loaded directly.
- If `cot.csv` is missing, the app fetches roughly the last 7 years of CFTC `legacy_fut` data and writes a new `cot.csv`.

This first run requires internet access to CFTC data sources.

## Utility script

Generate per-market CSV snapshots:

```bash
python generate_csvs.py
```

Outputs files under `cot/` for full history and a limited year range variant per market code.

## Notes

- The active market universe for the web app is currently hard-coded in `index.py`.
- Generated datasets can be large and are intentionally git-ignored.

## License

GNU General Public License v3.0. See `LICENSE`.
