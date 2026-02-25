import os
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor, as_completed
from flask import Flask, render_template, request, redirect, url_for, make_response
from flask_compress import Compress
import pandas as pd
from datetime import datetime
import time
from email.utils import parsedate_to_datetime
from willco import WillCo
from markets_loader import load_markets_safe

app = Flask(__name__)
Compress(app)

DEFAULT_LOW = 10
DEFAULT_HIGH = 90
VALID_MODES = {"all", "setups", "asset", "percentchange"}

csv_path = os.path.join(os.path.dirname(__file__), "cot.csv")
will_co = WillCo(csv_path)

# Load markets DataFrame once at module import time
MARKETS, MARKETS_LOAD_ERROR = load_markets_safe()

# Print error to console if loading failed
if MARKETS_LOAD_ERROR:
    print(f"CRITICAL ERROR: {MARKETS_LOAD_ERROR}")

_cached_csv_df = None
_cached_csv_mtime = None
_cached_csv_mtime_check = 0  # Track last mtime check time
_cached_results_df = None
_cached_results_mtime = None

# Use LRU cache for table HTML and filtered DataFrames (bottleneck #5.1 fix)
from functools import lru_cache

# Simple LRU cache class with maxsize
class LRUCache:
    def __init__(self, maxsize=32):
        self.cache = {}
        self.access_order = []
        self.maxsize = maxsize
    
    def get(self, key):
        if key in self.cache:
            # Move to end (most recently used)
            self.access_order.remove(key)
            self.access_order.append(key)
            return self.cache[key]
        return None
    
    def put(self, key, value):
        if key in self.cache:
            self.access_order.remove(key)
        elif len(self.cache) >= self.maxsize:
            # Remove least recently used (first item)
            oldest = self.access_order.pop(0)
            del self.cache[oldest]
        self.cache[key] = value
        self.access_order.append(key)
    
    def clear(self):
        self.cache.clear()
        self.access_order.clear()

_cached_table_html = LRUCache(maxsize=32)
_cached_filtered_df = LRUCache(maxsize=32)
MTIME_CHECK_INTERVAL = 5  # Only check mtime every 5 seconds

def get_csv_df():
    global _cached_csv_df, _cached_csv_mtime, _cached_csv_mtime_check
    current_time = time.time()
    
    # Only check mtime periodically to avoid excessive filesystem calls
    needs_check = (current_time - _cached_csv_mtime_check) > MTIME_CHECK_INTERVAL
    
    if needs_check:
        try:
            mtime = os.path.getmtime(csv_path)
            _cached_csv_mtime_check = current_time
        except OSError:
            _cached_csv_df = None
            _cached_csv_mtime = None
            return will_co.read_csv()

        if _cached_csv_df is None or _cached_csv_mtime != mtime:
            _cached_csv_df = will_co.read_csv()
            _cached_csv_mtime = mtime
    
    return _cached_csv_df

# Number of worker threads for parallel market calculations
MAX_WORKERS = 4

def _calculate_market_periods(args):
    """Helper function to calculate all periods for a single market."""
    csv_df, market = args
    frames = []
    for weeks in [26, 52, 104, 156, 208, 260]:
        frames.append(will_co.calculateWillCo(csv_df, market, weeks))
    return frames

def get_results_df():
    global _cached_results_df, _cached_results_mtime, _cached_table_html, _cached_filtered_df
    csv_df = get_csv_df()
    csv_mtime = _cached_csv_mtime

    if _cached_results_df is None or _cached_results_mtime != csv_mtime:
        # OPTIMIZATION: Use ThreadPoolExecutor for parallel market calculations
        markets = MARKETS['contract_code'].tolist()
        frames = []
        
        # Prepare arguments for parallel execution
        args_list = [(csv_df, market) for market in markets]
        
        # Use ThreadPoolExecutor to parallelize calculations
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = executor.map(_calculate_market_periods, args_list)
            for result_frames in futures:
                frames.extend(result_frames)
        
        _cached_results_df = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
        _cached_results_mtime = csv_mtime
        _cached_table_html.clear()
        _cached_filtered_df.clear()
    return _cached_results_df

def clamp(value, lower, upper):
    return max(lower, min(value, upper))

def normalize_thresholds(low, high):
    low = clamp(low, 0, 100)
    high = clamp(high, 0, 100)
    if low >= high:
        return DEFAULT_LOW, DEFAULT_HIGH
    return low, high

def parse_thresholds(values):
    try:
        low = int(values.get('low', DEFAULT_LOW))
    except (TypeError, ValueError):
        low = DEFAULT_LOW

    try:
        high = int(values.get('high', DEFAULT_HIGH))
    except (TypeError, ValueError):
        high = DEFAULT_HIGH

    return normalize_thresholds(low, high)

def parse_mode_and_asset(values):
    mode = values.get('mode', 'all')
    asset = values.get('asset')

    if mode not in VALID_MODES:
        return 'all', None

    if mode == 'asset':
        valid_assets = set(MARKETS['contract_name']) if not MARKETS.empty else set()
        if asset not in valid_assets:
            return 'all', None
        return 'asset', asset

    return mode, None

def color_index(val, low, high):
    if val <= low:
        return 'color: red'
    elif val >= high:
        return 'color:green'
    return 'color: white'

def color_percent(val, column):
    if column in ('commercials_net_(%)', 'large_speculators_net_(%)', 'small_speculators_net_(%)', 'commercials_change_(%)', 'large_speculators_change_(%)', 'small_speculators_change_(%)'):
        if val < 0:
            return 'color: red'
        elif val > 0:
            return 'color: green'
    return 'color: white'


def _compute_index_colors_vectorized(df, low, high):
    """
    Pre-compute color arrays for willco index columns using vectorized NumPy operations.
    This is much faster than using lambda functions per cell.
    
    Returns a DataFrame with same shape as subset columns, containing color strings.
    """
    import numpy as np
    
    index_cols = ['willco_commercials_index', 'willco_large_specs_index', 'willco_small_specs_index']
    available_cols = [col for col in index_cols if col in df.columns]
    
    if not available_cols:
        return pd.DataFrame(index=df.index)
    
    # Create color DataFrame with default white
    color_df = pd.DataFrame('color: white', index=df.index, columns=available_cols)
    
    for col in available_cols:
        values = df[col].values
        # Vectorized: red where val <= low, green where val >= high, else white
        # NOTE: Using 'color:green' (no space) to match original color_index() function
        colors = np.where(values <= low, 'color: red',
                np.where(values >= high, 'color:green', 'color: white'))
        color_df[col] = colors
    
    return color_df


def _compute_percent_colors_vectorized(df):
    """
    Pre-compute color arrays for percent columns using vectorized NumPy operations.
    
    Returns a DataFrame with same shape as percent columns, containing color strings.
    """
    import numpy as np
    
    percent_columns = ['commercials_net_(%)', 'large_speculators_net_(%)', 'small_speculators_net_(%)',
                       'commercials_change_(%)', 'large_speculators_change_(%)', 'small_speculators_change_(%)']
    available_cols = [col for col in percent_columns if col in df.columns]
    
    if not available_cols:
        return pd.DataFrame(index=df.index)
    
    # Create color DataFrame with default white
    color_df = pd.DataFrame('color: white', index=df.index, columns=available_cols)
    
    for col in available_cols:
        values = df[col].values
        # Vectorized: red where val < 0, green where val > 0, else white
        colors = np.where(values < 0, 'color: red',
                np.where(values > 0, 'color: green', 'color: white'))
        color_df[col] = colors
    
    return color_df

def generateTable(filter_mode, selected_name=None, low=DEFAULT_LOW, high=DEFAULT_HIGH):
    result = get_results_df()
    cache_key = (_cached_results_mtime, filter_mode, low, high, selected_name)
    cached_html = _cached_table_html.get(cache_key)
    if cached_html is not None:
        return cached_html
    
    cached_filtered = _cached_filtered_df.get(cache_key)
    if cached_filtered is not None:
        result = cached_filtered
    else:
        if filter_mode == 'setups':
            if 'willco_commercials_index' in result.columns:
                # OPTIMIZATION: Use df.query() for more efficient filtering
                query = f'(willco_commercials_index >= {high} or willco_commercials_index <= {low}) or (willco_large_specs_index >= {high} or willco_large_specs_index <= {low}) or (willco_small_specs_index >= {high} or willco_small_specs_index <= {low})'
                result = result.query(query)
        elif filter_mode == 'asset':
            if 'market_and_exchange_names' in result.columns:
                # OPTIMIZATION: Use df.query() for more efficient filtering
                result = result.query(f'market_and_exchange_names == "{selected_name}"')
        elif filter_mode == 'percentchange':
            if all(col in result.columns for col in ['commercials_change_(%)', 'large_speculators_change_(%)', 'small_speculators_change_(%)']):
                # OPTIMIZATION: Use df.query() for more efficient filtering
                # Use backticks to escape column names with special characters
                query = '`commercials_change_(%)` >= 5 or `commercials_change_(%)` <= -5 or `large_speculators_change_(%)` >= 5 or `large_speculators_change_(%)` <= -5 or `small_speculators_change_(%)` >= 5 or `small_speculators_change_(%)` <= -5'
                result = result.query(query)
        
        # Use put() method which handles LRU eviction automatically
        _cached_filtered_df.put(cache_key, result)

    if result.empty:
        styled_html = "<p>No data available.</p>"
    else:
        # OPTIMIZATION: Pre-compute all color arrays using vectorized NumPy operations
        # This is much faster than calling a Python function per cell
        index_colors = _compute_index_colors_vectorized(result, low, high)
        percent_colors = _compute_percent_colors_vectorized(result)
        
        styled = result.style
        
        # Apply index column colors using .apply() which works on entire columns
        # This is more efficient than .map() which calls function per cell
        index_cols = ['willco_commercials_index', 'willco_large_specs_index', 'willco_small_specs_index']
        for col in index_cols:
            if col in result.columns and col in index_colors.columns:
                # .apply() passes the entire column as a Series, we return a Series of colors
                def make_col_mapper(color_series):
                    def mapper(col):
                        return color_series.values
                    return mapper
                styled = styled.apply(make_col_mapper(index_colors[col]), axis=0, subset=[col])
        
        # Apply percent column colors using .apply()
        percent_cols = ['commercials_net_(%)', 'large_speculators_net_(%)', 'small_speculators_net_(%)',
                       'commercials_change_(%)', 'large_speculators_change_(%)', 'small_speculators_change_(%)']
        for col in percent_cols:
            if col in result.columns and col in percent_colors.columns:
                def make_col_mapper(color_series):
                    def mapper(col):
                        return color_series.values
                    return mapper
                styled = styled.apply(make_col_mapper(percent_colors[col]), axis=0, subset=[col])
        
        styled_html = styled.to_html(index=False, escape=False)

    # Use put() method which handles LRU eviction automatically
    _cached_table_html.put(cache_key, styled_html)
    return styled_html

# Track last data modification time for HTTP caching
_last_data_mtime = time.time()

@app.route('/')
def index():
    global _last_data_mtime
    low, high = parse_thresholds(request.args)
    mode, selected_asset = parse_mode_and_asset(request.args)
    
    # Get dropdown options, handle empty MARKETS DataFrame
    dropdown_options = MARKETS['contract_name'] if not MARKETS.empty else []
    
    # Check if there's a markets loading error to display
    error_message = MARKETS_LOAD_ERROR if MARKETS_LOAD_ERROR else None
    
    # OPTIMIZATION: Check If-Modified-Since header (bottleneck #8.1 fix)
    if_none_match = request.headers.get('If-None-Match')
    if_modified_since = request.headers.get('If-Modified-Since')
    
    # Generate ETag based on current parameters
    current_etag = f'"{mode}-{low}-{high}-{selected_asset}"'
    
    # Check if client has cached version
    if if_none_match and if_none_match == current_etag:
        # Also check If-Modified-Since
        if if_modified_since:
            try:
                client_time = parsedate_to_datetime(if_modified_since)
                server_time = datetime.fromtimestamp(_last_data_mtime)
                if client_time >= server_time:
                    return '', 304  # Not Modified
            except (ValueError, TypeError):
                pass  # Invalid date, proceed normally
    
    # Generate the table
    table_html = generateTable(mode, selected_name=selected_asset, low=low, high=high)
    
    response = make_response(render_template(
        'index.html',
        table_html=table_html,
        dropdown_options=dropdown_options,
        selected_asset=selected_asset,
        low=low,
        high=high,
        mode=mode,
        error_message=error_message
    ))
    
    # Set caching headers
    response.headers['Cache-Control'] = 'public, max-age=60'
    response.headers['Last-Modified'] = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
    response.headers['ETag'] = current_etag
    return response

@app.route('/fetch_and_store', methods=['POST'])
def store_data():
    low, high = parse_thresholds(request.form)
    mode, selected_asset = parse_mode_and_asset(request.form)
    will_co.fetch_and_store_cot_data()
    query_params = {'low': low, 'high': high, 'mode': mode}
    if mode == 'asset' and selected_asset:
        query_params['asset'] = selected_asset
    return redirect(url_for('index', **query_params))

@app.route('/indexfilter', methods=['POST'])
def indexfilter():
    low, high = parse_thresholds(request.form)
    return redirect(url_for('index', mode='setups', low=low, high=high))

@app.route('/percentchangefilter', methods=['POST'])
def percentchangefilter():
    low, high = parse_thresholds(request.form)
    dropdown_options = MARKETS['contract_name'] if not MARKETS.empty else []
    return render_template(
        'index.html',
        table_html=generateTable('percentchange', low=low, high=high),
        dropdown_options=dropdown_options,
        selected_asset=None,
        low=low,
        high=high,
        mode='percentchange'
    )

@app.route('/assetfilter', methods=['POST'])
def assetfilter():
    low, high = parse_thresholds(request.form)
    selected_asset = request.form.get('asset')
    query_params = {'mode': 'asset', 'low': low, 'high': high}
    if selected_asset:
        query_params['asset'] = selected_asset
    return redirect(url_for('index', **query_params))

@app.route('/nofilter', methods=['POST'])
def nofilter():
    return redirect(url_for('index'))

@app.route('/resources')
def resources():
    return render_template('resources.html')

if __name__ == '__main__':
    app.run(debug=True)
