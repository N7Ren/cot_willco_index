# cot_willco_index

`cot_willco_index` is a Flask app that builds and displays Williams Commercial Index-style signals from CFTC legacy futures Commitments of Traders (COT) data.

## Current repository analysis

The current codebase is a compact single-app layout with three active source files:

- `index.py`: Flask routes, hard-coded market list, table generation, and UI filtering behavior
- `willco.py`: COT data fetch/storage and WillCo metric calculation logic
- `templates/index.html`: Bootstrap-based UI template

Current tracked repo files:

- `index.py`
- `willco.py`
- `templates/index.html`
- `markets.csv` - Market configuration file (see [MARKETS_GUIDE.md](MARKETS_GUIDE.md))
- `README.md`
- `LICENSE`

## Functional behavior

The app:

- Uses `cot_reports` to pull `legacy_fut` data
- Persists data to local `cot.csv`
- Calculates net exposure and WillCo-style index scores (`0-100`) for:
  - Commercials
  - Large Speculators (Non-Commercials)
  - Small Speculators (Non-Reportables)
- Computes values over these lookbacks:
  - 26 weeks (0.5y)
  - 52 weeks (1y)
  - 104 weeks (2y)
  - 156 weeks (3y)
  - 208 weeks (4y)
  - 260 weeks (5y)
- Renders a table with color highlighting and filters

## Data flow

1. `WillCo` initializes with `cot.csv` path.
2. If `cot.csv` does not exist, it fetches roughly 7 years of COT data and writes `cot.csv`.
3. Flask loads CSV data and computes per-market results for all lookbacks.
4. Results are rendered in the HTML table.

## Routes and UI actions

- `GET /`: full unfiltered table
- `POST /fetch_and_store`: refresh local COT data
- `POST /indexfilter`: show extreme index setups
- `POST /assetfilter`: show selected asset only
- `POST /nofilter`: clear filters and return to full table

Note: `POST /percentchangefilter` exists in code but is not currently wired to a visible button in `templates/index.html`.

## Requirements

- Python 3.10+
- `flask`
- `pandas`
- `cot-reports`

Recommended install (works on externally managed Python environments such as Debian/Ubuntu):

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install flask pandas cot-reports
```

## Run

```bash
. .venv/bin/activate
python index.py
```

Open `http://127.0.0.1:5000`.

## Implementation notes

- Market universe is configured in `markets.csv` (see [MARKETS_GUIDE.md](MARKETS_GUIDE.md) for how to customize).
- `cot.csv` is expected at repository root and is generated on first run if missing.
- The app runs with `debug=True` in `index.py`.

## Customizing Markets

The application loads its market list from `markets.csv`, which can be easily edited to add, remove, or modify markets without changing any code. See [MARKETS_GUIDE.md](MARKETS_GUIDE.md) for detailed instructions on how to customize the market list.

## License

GNU General Public License v3.0. See `LICENSE`.
