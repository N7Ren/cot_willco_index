# cot_willco_index

`cot_willco_index` is a static web application that builds and displays Williams Commercial Index-style signals from CFTC legacy futures Commitments of Traders (COT) data.

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
- Renders a purely static table with instant JavaScript-based filtering and highlighting

## Usage

### Generate Data
Run the build script to fetch the latest COT data, calculate all indices, and export them to JSON:
```bash
python3 build.py
```

### View Dashboard
Open `index.html` in your browser. Since it uses the Fetch API to load `data.json`, it is best viewed via a local web server:
```bash
# Using Python
python3 -m http.server 8000
# Then visit http://localhost:8000/index.html
```

## Architecture

- **`build.py`**: Static site generator. It updates `cot.csv`, calculates metrics, and outputs `data.json`.
- **`willco.py`**: Core logic for COT data processing and WillCo Index calculations.
- **`index.html`**: Purely static frontend with JavaScript-based filtering and rendering.
- **`resources.html`**: Static resources and documentation page.
- **`markets.csv`**: Configuration file for tracked commodity markets.
- **`cot.csv`**: Local cache of downloaded COT data.
- **`data.json`**: Pre-calculated data exported for the frontend.

## Requirements

- Python 3.10+
- `pandas`
- `numpy`
- `cot-reports`

Recommended install:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Customizing Markets

The application loads its market list from `markets.csv`. See [MARKETS_GUIDE.md](MARKETS_GUIDE.md) for detailed instructions on how to customize the market list.

## License

GNU General Public License v3.0. See `LICENSE`.
