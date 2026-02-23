import os
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
    if column == 'commercials_net_(%)' or 'large_speculators_net_(%)' or 'small_speculators_net_(%)' or 'commercials_change_(%)' or 'large_speculators_change_(%)' or 'small_speculators_change_(%)':
        if val < 0:
            return 'color: red'
        elif val > 0:
            return 'color: green'
    return 'color: white'

def generateTable(filter_mode, selected_name=None, low=DEFAULT_LOW, high=DEFAULT_HIGH):
    csv_df = will_co.read_csv()
    
    frames = []

    for market in list(markets['contract_code']):
        frames.append(will_co.calculateWillCo(csv_df, market, 26))
        frames.append(will_co.calculateWillCo(csv_df, market, 52))
        frames.append(will_co.calculateWillCo(csv_df, market, 104))
        frames.append(will_co.calculateWillCo(csv_df, market, 156))
        frames.append(will_co.calculateWillCo(csv_df, market, 208))
        frames.append(will_co.calculateWillCo(csv_df, market, 260))

    result = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
        
    if filter_mode == 'setups':
        result = result[(result['willco_commercials_index'] >= high) | (result['willco_commercials_index'] <= low) | ((result['willco_large_specs_index'] >= high) | (result['willco_large_specs_index'] <= low)) | ((result['willco_small_specs_index'] >= high) | (result['willco_small_specs_index'] <= low))]
    elif filter_mode == 'percentchange':
        result = result[(result['commercials_change_(%)'] >= 5) | (result['commercials_change_(%)'] <= -5) | ((result['large_speculators_change_(%)'] >= 5) | (result['large_speculators_change_(%)'] <= -5)) | ((result['small_speculators_change_(%)'] >= 5) | (result['small_speculators_change_(%)'] <= -5))]
    elif filter_mode == 'asset':
        result = result[result['market_and_exchange_names'] == selected_name]

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
