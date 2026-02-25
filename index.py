import os
from collections import OrderedDict
from flask import Flask, render_template, request, redirect, url_for, make_response
from flask_compress import Compress
import pandas as pd
from datetime import datetime
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
_cached_results_df = None
_cached_results_mtime = None
_cached_table_html = OrderedDict()
_cached_filtered_df = OrderedDict()
MAX_TABLE_CACHE_ENTRIES = 32
MAX_FILTERED_CACHE_ENTRIES = 32

def get_csv_df():
    global _cached_csv_df, _cached_csv_mtime
    try:
        mtime = os.path.getmtime(csv_path)
    except OSError:
        _cached_csv_df = None
        _cached_csv_mtime = None
        return will_co.read_csv()

    if _cached_csv_df is None or _cached_csv_mtime != mtime:
        _cached_csv_df = will_co.read_csv()
        _cached_csv_mtime = mtime
    return _cached_csv_df

def get_results_df():
    global _cached_results_df, _cached_results_mtime, _cached_table_html, _cached_filtered_df
    csv_df = get_csv_df()
    csv_mtime = _cached_csv_mtime

    if _cached_results_df is None or _cached_results_mtime != csv_mtime:
        frames = []
        for market in MARKETS['contract_code']:
            frames.append(will_co.calculateWillCo(csv_df, market, 26))
            frames.append(will_co.calculateWillCo(csv_df, market, 52))
            frames.append(will_co.calculateWillCo(csv_df, market, 104))
            frames.append(will_co.calculateWillCo(csv_df, market, 156))
            frames.append(will_co.calculateWillCo(csv_df, market, 208))
            frames.append(will_co.calculateWillCo(csv_df, market, 260))
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

def generateTable(filter_mode, selected_name=None, low=DEFAULT_LOW, high=DEFAULT_HIGH):
    result = get_results_df()
    cache_key = (_cached_results_mtime, filter_mode, low, high, selected_name)
    cached_html = _cached_table_html.get(cache_key)
    if cached_html is not None:
        _cached_table_html.move_to_end(cache_key)
        return cached_html
    
    cached_filtered = _cached_filtered_df.get(cache_key)
    if cached_filtered is not None:
        _cached_filtered_df.move_to_end(cache_key)
        result = cached_filtered  # Optimized: removed unnecessary .copy()
    else:
        if filter_mode == 'setups':
            if 'willco_commercials_index' in result.columns:
                mask_commercial = (result['willco_commercials_index'] >= high) | (result['willco_commercials_index'] <= low)
                mask_large_specs = (result['willco_large_specs_index'] >= high) | (result['willco_large_specs_index'] <= low)
                mask_small_specs = (result['willco_small_specs_index'] >= high) | (result['willco_small_specs_index'] <= low)
                result = result[mask_commercial | mask_large_specs | mask_small_specs]
        elif filter_mode == 'asset':
            if 'market_and_exchange_names' in result.columns:
                result = result[result['market_and_exchange_names'] == selected_name]
        elif filter_mode == 'percentchange':
            if all(col in result.columns for col in ['commercials_change_(%)', 'large_speculators_change_(%)', 'small_speculators_change_(%)']):
                mask_commercials_change = (result['commercials_change_(%)'] >= 5) | (result['commercials_change_(%)'] <= -5)
                mask_large_specs_change = (result['large_speculators_change_(%)'] >= 5) | (result['large_speculators_change_(%)'] <= -5)
                mask_small_specs_change = (result['small_speculators_change_(%)'] >= 5) | (result['small_speculators_change_(%)'] <= -5)
                result = result[mask_commercials_change | mask_large_specs_change | mask_small_specs_change]
        
        _cached_filtered_df[cache_key] = result
        if len(_cached_filtered_df) > MAX_FILTERED_CACHE_ENTRIES:
            _cached_filtered_df.popitem(last=False)

    if result.empty:
        styled_html = "<p>No data available.</p>"
    else:
        styled = result.style.map(lambda val: color_index(val, low, high), subset=['willco_commercials_index', 'willco_large_specs_index', 'willco_small_specs_index'])
        # Apply color_percent to each column individually
        percent_columns = ['commercials_net_(%)', 'large_speculators_net_(%)', 'small_speculators_net_(%)',
                          'commercials_change_(%)', 'large_speculators_change_(%)', 'small_speculators_change_(%)']
        for col in percent_columns:
            if col in result.columns:
                styled = styled.map(lambda val, column=col: color_percent(val, column), subset=[col])
        styled_html = styled.to_html(index=False, escape=False)

    _cached_table_html[cache_key] = styled_html
    if len(_cached_table_html) > MAX_TABLE_CACHE_ENTRIES:
        _cached_table_html.popitem(last=False)
    return styled_html

@app.route('/')
def index():
    low, high = parse_thresholds(request.args)
    mode, selected_asset = parse_mode_and_asset(request.args)
    
    # Get dropdown options, handle empty MARKETS DataFrame
    dropdown_options = MARKETS['contract_name'] if not MARKETS.empty else []
    
    # Check if there's a markets loading error to display
    error_message = MARKETS_LOAD_ERROR if MARKETS_LOAD_ERROR else None
    
    # Optimized: Add HTTP caching headers for better performance
    response = make_response(render_template(
        'index.html',
        table_html=generateTable(mode, selected_name=selected_asset, low=low, high=high),
        dropdown_options=dropdown_options,
        selected_asset=selected_asset,
        low=low,
        high=high,
        mode=mode,
        error_message=error_message
    ))
    response.headers['Cache-Control'] = 'public, max-age=60'
    response.headers['Last-Modified'] = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
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
