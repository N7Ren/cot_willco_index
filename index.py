import os
from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import sqlite3
from markets import markets
from willco import WillCo

app = Flask(__name__)

db_path = os.path.join(os.path.dirname(__file__), "cot.db")
will_co = WillCo(db_path)

def color_index(val, column):
    if val <= 5 or val >= 95:
        if column == 'c_index_0_5y' or 'c_index_1y' or 'c_index_2y' or 'c_index_3y' or 'c_index_4y' or 'c_index_5y':
            return 'color: red'
        elif column == 'nc_index_0_5y' or 'nc_index_1y' or 'nc_index_2y' or 'nc_index_3y' or 'nc_index_4y' or 'nc_index_5y':
            return 'color: #3498db'
        elif column == 'nr_index_0_5y' or 'nr_index_1y' or 'nr_index_2y' or 'nr_index_3y' or 'nr_index_4y' or 'nr_index_5y':
            return 'color: yellow'
    return 'color: white'

def generateTable(filter, selected_name=None):
    connection = sqlite3.connect(db_path)
    result = pd.DataFrame()

    for market in list(markets['contract_code']):
        query = """SELECT market_and_exchange_names, c_index_0_5y, nc_index_0_5y, nr_index_0_5y, c_index_1y, nc_index_1y, nr_index_1y, c_index_2y, nc_index_2y, nr_index_2y, 
        c_index_3y, nc_index_3y, nr_index_3y, c_index_4y, nc_index_4y, nr_index_4y, c_index_5y, nc_index_5y, nr_index_5y, as_of_date_in_form_yyyy_mm_dd
        FROM cot_table WHERE cftc_contract_market_code = ? ORDER BY id desc LIMIT 1"""
        df = pd.read_sql_query(query, connection, params=(market,))
        result = pd.concat([result, df], ignore_index=True)
    
    connection.close()

    if filter == 1:
        result = result[(result['willco_commercials_index_0_5y'] >= 95) | (result['willco_commercials_index_0_5y'] <= 5) | 
                        ((result['willco_large_specs_index_0_5y'] >= 95) | (result['willco_large_specs_index_0_5y'] <= 5)) | 
                        ((result['willco_small_specs_index_0_5y'] >= 95) | (result['willco_small_specs_index_0_5y'] <= 5)) | 
                        (result['willco_commercials_index_1y'] >= 95) | (result['willco_commercials_index_1y'] <= 5) | 
                        ((result['willco_large_specs_index_1y'] >= 95) | (result['willco_large_specs_index_1y'] <= 5)) | 
                        ((result['willco_small_specs_index_1y'] >= 95) | (result['willco_small_specs_index_1y'] <= 5))
                        ]
    elif filter == 2:
        query = """SELECT market_and_exchange_names, c_index_0_5y, nc_index_0_5y, nr_index_0_5y, c_index_1y, nc_index_1y, nr_index_1y, c_index_2y, nc_index_2y, nr_index_2y, 
        c_index_3y, nc_index_3y, nr_index_3y, c_index_4y, nc_index_4y, nr_index_4y, c_index_5y, nc_index_5y, nr_index_5y, as_of_date_in_form_yyyy_mm_dd
        FROM cot_table WHERE market_and_exchange_names = ? ORDER BY id desc"""
        result = pd.read_sql_query(query, connection, params=(selected_name,))

    styled_df = result.style.map(lambda val: color_index(val, 'c_index_0_5y'), subset='c_index_0_5y')\
                        .map(lambda val: color_index(val, 'nc_index_0_5y'), subset='nc_index_0_5y')\
                        .map(lambda val: color_index(val, 'nr_index_0_5y'), subset='nr_index_0_5y')\
                        .map(lambda val: color_index(val, 'c_index_1y'), subset='c_index_1y')\
                        .map(lambda val: color_index(val, 'nc_index_1y'), subset='nc_index_1y')\
                        .map(lambda val: color_index(val, 'nr_index_1y'), subset='nr_index_1y')\
                        .map(lambda val: color_index(val, 'c_index_2y'), subset='c_index_2y')\
                        .map(lambda val: color_index(val, 'nc_index_2y'), subset='nc_index_2y')\
                        .map(lambda val: color_index(val, 'nr_index_2y'), subset='nr_index_2y')\
                        .map(lambda val: color_index(val, 'c_index_3y'), subset='c_index_3y')\
                        .map(lambda val: color_index(val, 'nc_index_3y'), subset='nc_index_3y')\
                        .map(lambda val: color_index(val, 'nr_index_3y'), subset='nr_index_3y')\
                        .map(lambda val: color_index(val, 'c_index_4y'), subset='c_index_4y')\
                        .map(lambda val: color_index(val, 'nc_index_4y'), subset='nc_index_4y')\
                        .map(lambda val: color_index(val, 'nr_index_4y'), subset='nr_index_4y')\
                        .map(lambda val: color_index(val, 'c_index_5y'), subset='c_index_5y')\
                        .map(lambda val: color_index(val, 'nc_index_5y'), subset='nc_index_5y')\
                        .map(lambda val: color_index(val, 'nr_index_5y'), subset='nr_index_5y')

    styled_html = styled_df.to_html(escape=False, index=False, classes='styled-table table table-bordered table-hover')

    return styled_html

@app.route('/')
def index():
    dropdown_options = markets['contract_names']
    return render_template('index.html', table_html=generateTable(False), dropdown_options=dropdown_options)

@app.route('/fetch_and_store', methods=['POST'])
def store_data():
    will_co.fetch_and_store_cot_data()
    will_co.calculateWillCo(markets);
    return redirect('/')

@app.route('/indexfilter', methods=['POST'])
def indexfilter():
    return render_template('index.html', table_html=generateTable(1))

@app.route('/assetfilter', methods=['POST'])
def assetfilter():
    selected_name = request.form.get('asset_dropdown')
    return render_template('index.html', table_html=generateTable(2, selected_name))

@app.route('/nofilter', methods=['POST'])
def nofilter():
    return redirect('/') 

if __name__ == '__main__':
    app.run(debug=True)

