import os
from collections import OrderedDict
from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
from willco import WillCo

app = Flask(__name__)

DEFAULT_LOW = 10
DEFAULT_HIGH = 90
VALID_MODES = {"all", "setups", "asset"}

csv_path = os.path.join(os.path.dirname(__file__), "cot.csv")
will_co = WillCo(csv_path)

markets = pd.DataFrame({
    'contract_code': ['098662', '042601', '044601', '043602', '020601', 
                      '232741', '102741', '096742', '090741', '099741', '097741', '092741', '112741', '095741', '122741', '299741', '399741',
                      '088691', '084691', '075651', '076651', '067651', '023651', '002602', '073732', '083731', '005602',
                      '124603', '209742', '13874A', '239742', '240741', '244042', 
                      '133741', '146021'],
    'contract_names':  ['USD INDEX', 'UST 2Y NOTE', 'UST 5Y NOTE', 'UST 10Y NOTE', 'UST BOND', 
                        'AUSTRALIAN DOLLAR', 'BRAZILIAN REAL', 'BRITISH POUND', 'CANADIAN DOLLAR', 'EURO FX', 'JAPANESE YEN', 'SWISS FRANC', 'NZ DOLLAR', 'MEXICAN PESO', 'SO AFRICAN RAND', 'EUR FX/GBP', 'EURO FX/JPY',
                        'GOLD', 'SILVER', 'PALLADIUM', 'PLATINUM', 'WTI-PHYSICAL', 'NAT GAS NYME', 'CORN', 'COCOA', 'COFFEE C', 'SOYBEANS',
                        'DJIA x $5', 'NASDAQ MINI', 'E-MINI S&P 500', 'RUSSELL E-MINI', 'NIKKEI STOCK AVERAGE', 'MSCI EM INDEX', 
                        'BITCOIN', 'ETHER CASH SETTLED']
})

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
        for market in list(markets['contract_code']):
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
        valid_assets = set(markets['contract_names'])
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
        result = cached_filtered
    else:
        if filter_mode == 'setups':
            result = result[(result['willco_commercials_index'] >= high) | (result['willco_commercials_index'] <= low) | ((result['willco_large_specs_index'] >= high) | (result['willco_large_specs_index'] <= low)) | ((result['willco_small_specs_index'] >= high) | (result['willco_small_specs_index'] <= low))]
        elif filter_mode == 'percentchange':
            result = result[(result['commercials_change_(%)'] >= 5) | (result['commercials_change_(%)'] <= -5) | ((result['large_speculators_change_(%)'] >= 5) | (result['large_speculators_change_(%)'] <= -5)) | ((result['small_speculators_change_(%)'] >= 5) | (result['small_speculators_change_(%)'] <= -5))]
        elif filter_mode == 'asset':
            result = result[result['market_and_exchange_names'] == selected_name]
        
        _cached_filtered_df[cache_key] = result.copy()
        if len(_cached_filtered_df) > MAX_FILTERED_CACHE_ENTRIES:
            _cached_filtered_df.popitem(last=False)

    styled_df = result.style.map(lambda val: color_index(val, low, high), subset='willco_commercials_index')\
                        .map(lambda val: color_index(val, low, high), subset='willco_large_specs_index')\
                        .map(lambda val: color_index(val, low, high), subset='willco_small_specs_index')\
                        .map(lambda val: color_percent(val, 'commercials_net_(%)'), subset='commercials_net_(%)')\
                        .map(lambda val: color_percent(val, 'large_speculators_net_(%)'), subset='large_speculators_net_(%)')\
                        .map(lambda val: color_percent(val, 'small_speculators_net_(%)'), subset='small_speculators_net_(%)')\
                        .map(lambda val: color_percent(val, 'commercials_change_(%)'), subset='commercials_change_(%)')\
                        .map(lambda val: color_percent(val, 'large_speculators_change_(%)'), subset='large_speculators_change_(%)')\
                        .map(lambda val: color_percent(val, 'small_speculators_change_(%)'), subset='small_speculators_change_(%)')

    styled_html = styled_df.to_html(escape=False, index=False, classes='styled-table table table-bordered table-hover')

    _cached_table_html[cache_key] = styled_html
    if len(_cached_table_html) > MAX_TABLE_CACHE_ENTRIES:
        _cached_table_html.popitem(last=False)
    return styled_html

@app.route('/')
def index():
    low, high = parse_thresholds(request.args)
    mode, selected_asset = parse_mode_and_asset(request.args)
    dropdown_options = markets['contract_names']
    return render_template(
        'index.html',
        table_html=generateTable(mode, selected_name=selected_asset, low=low, high=high),
        dropdown_options=dropdown_options,
        selected_asset=selected_asset,
        low=low,
        high=high,
        mode=mode
    )

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
    return render_template(
        'index.html',
        table_html=generateTable('percentchange', low=low, high=high),
        dropdown_options=markets['contract_names'],
        selected_asset=None,
        low=low,
        high=high,
        mode='all'
    )

@app.route('/assetfilter', methods=['POST'])
def assetfilter():
    low, high = parse_thresholds(request.form)
    selected_name = request.form.get('asset_dropdown') or request.form.get('asset')
    valid_assets = set(markets['contract_names'])
    if selected_name not in valid_assets:
        return redirect(url_for('index', mode='all', low=low, high=high))
    return redirect(url_for('index', mode='asset', asset=selected_name, low=low, high=high))

@app.route('/nofilter', methods=['POST'])
def nofilter():
    low, high = parse_thresholds(request.form)
    return redirect(url_for('index', mode='all', low=low, high=high))

@app.route('/resources')
def resources():
    return render_template('resources.html')

if __name__ == '__main__':
    app.run(debug=True)
