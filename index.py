import os
from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
from willco import WillCo

app = Flask(__name__)

csv_path = os.path.join(os.path.dirname(__file__), "cot.csv")
will_co = WillCo(csv_path)

#'NAT GAS NYME', '023651',
#'BRAZILIAN REAL', '102741',

markets = pd.DataFrame({
    'contract_code': ['098662', '042601', '044601', '043602', '020601', 
                      '232741', '096742', '090741', '099741', '097741', '092741', '112741', '095741', '122741', '299741', '399741',
                      '088691', '084691', '075651', '076651', '067651', '002602', '073732', '083731', '005602', 
                      '124603', '209742', '13874A', '239742', '240741', '244042', 
                      '133741', '146021'],
    'contract_names':  ['USD INDEX', 'UST 2Y NOTE', 'UST 5Y NOTE', 'UST 10Y NOTE', 'UST BOND', 
                        'AUSTRALIAN DOLLAR', 'BRITISH POUND', 'CANADIAN DOLLAR', 'EURO FX', 'JAPANESE YEN', 'SWISS FRANC', 'NZ DOLLAR', 'MEXICAN PESO', 'SO AFRICAN RAND', 'EUR FX/GBP', 'EURO FX/JPY',
                        'GOLD', 'SILVER', 'PALLADIUM', 'PLATINUM', 'WTI-PHYSICAL', 'CORN', 'COCOA', 'COFFEE C', 'SOYBEANS',
                        'DJIA x $5', 'NASDAQ MINI', 'E-MINI S&P 500', 'RUSSELL E-MINI', 'NIKKEI STOCK AVERAGE', 'MSCI EM INDEX', 
                        'BITCOIN', 'ETHER CASH SETTLED']
})

def color_index(val, column):
    if val <= 5:
        return 'color: red'
    elif val >= 95:
        return 'color:green'
    return 'color: white'

def color_percent(val, column):
    if column == 'commercials_net_(%)' or 'large_speculators_net_(%)' or 'small_speculators_net_(%)' or 'commercials_change_(%)' or 'large_speculators_change_(%)' or 'small_speculators_change_(%)':
        if val < 0:
            return 'color: red'
        elif val > 0:
            return 'color: green'
    return 'color: white'

def generateTable(filter, selected_name=None):
    csv_df = will_co.read_csv()
    
    result = pd.DataFrame()

    for market in list(markets['contract_code']):
        df = will_co.calculateWillCo(csv_df, market, 26)
        result = pd.concat([result, df], ignore_index=True)
        df = will_co.calculateWillCo(csv_df, market, 52)
        result = pd.concat([result, df], ignore_index=True)
        df = will_co.calculateWillCo(csv_df, market, 104)
        result = pd.concat([result, df], ignore_index=True)
        df = will_co.calculateWillCo(csv_df, market, 156)
        result = pd.concat([result, df], ignore_index=True)
        df = will_co.calculateWillCo(csv_df, market, 208)
        result = pd.concat([result, df], ignore_index=True)
        df = will_co.calculateWillCo(csv_df, market, 260)
        result = pd.concat([result, df], ignore_index=True)
        
    if filter == 1:
        result = result[(result['willco_commercials_index'] >= 95) | (result['willco_commercials_index'] <= 5) | ((result['willco_large_specs_index'] >= 95) | (result['willco_large_specs_index'] <= 5)) | ((result['willco_small_specs_index'] >= 95) | (result['willco_small_specs_index'] <= 5))]
    elif filter == 2:
        result = result[(result['commercials_change_(%)'] >= 5) | (result['commercials_change_(%)'] <= -5) | ((result['large_speculators_change_(%)'] >= 5) | (result['large_speculators_change_(%)'] <= -5)) | ((result['small_speculators_change_(%)'] >= 5) | (result['small_speculators_change_(%)'] <= -5))]
    elif filter == 3:
        result = result[result['market_and_exchange_names'] == selected_name]

    styled_df = result.style.map(lambda val: color_index(val, 'willco_commercials_index'), subset='willco_commercials_index')\
                        .map(lambda val: color_index(val, 'willco_large_specs_index'), subset='willco_large_specs_index')\
                        .map(lambda val: color_index(val, 'willco_small_specs_index'), subset='willco_small_specs_index')\
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
    dropdown_options = markets['contract_names']
    return render_template('index.html', table_html=generateTable(False), dropdown_options=dropdown_options)

@app.route('/fetch_and_store', methods=['POST'])
def store_data():
    will_co.fetch_and_store_cot_data()
    return redirect('/')

@app.route('/indexfilter', methods=['POST'])
def indexfilter():
    dropdown_options = markets['contract_names']
    return render_template('index.html', table_html=generateTable(1), dropdown_options=dropdown_options)

@app.route('/percentchangefilter', methods=['POST'])
def percentchangefilter():
    dropdown_options = markets['contract_names']
    return render_template('index.html', table_html=generateTable(2), dropdown_options=dropdown_options)

@app.route('/assetfilter', methods=['POST'])
def assetfilter():
    selected_name = request.form.get('asset_dropdown')
    dropdown_options = markets['contract_names']
    return render_template('index.html', table_html=generateTable(3, selected_name), dropdown_options=dropdown_options)

@app.route('/nofilter', methods=['POST'])
def nofilter():
    return redirect('/') 

if __name__ == '__main__':
    app.run(debug=True)

