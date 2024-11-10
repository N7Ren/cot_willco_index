import os
import cot_reports as cot
import pandas as pd
import datetime
import sqlite3
from markets import markets

class WillCo:

    def __init__(self, db_path):        
        self.db_path = db_path
        if not os.path.exists(self.db_path):
            self.fetch_and_store_cot_data()
            self.will_co.calculateWillCo(markets);
    
    def fetch_and_store_cot_data(self):
        df = pd.DataFrame()
        begin_year = 2017
        end_year = 2024

        for i in range(begin_year, end_year + 1):
            single_year = pd.DataFrame(cot.cot_year(i, cot_report_type='legacy_fut')) 
            df = pd.concat([df, single_year], ignore_index=True)

        df = df.rename(columns=lambda x: x.replace(' ', '_').replace('-', '_').replace('(', '_').replace(')', '_').lower())
        df.replace('.', 0, inplace=True)

        df['market_and_exchange_names'] = df['market_and_exchange_names'].str.split(' - ', expand=True)[0]

        df['commercials_net_value'] = df["commercial_positions_long__all_"] - df["commercial_positions_short__all_"]
        df['large_speculators_net_value'] = df["noncommercial_positions_long__all_"] - df["noncommercial_positions_short__all_"]
        df['small_speculators_net_value'] = df["nonreportable_positions_long__all_"] - df["nonreportable_positions_short__all_"]

        df['commercials_net_change'] = df['change_in_commercial_long__all_'].astype(int) - df['change_in_commercial_short__all_'].astype(int)
        df['large_speculators_net_change'] = df['change_in_noncommercial_long__all_'].astype(int) - df['change_in_noncommercial_short__all_'].astype(int)
        df['small_speculators_net_change'] = df['change_in_nonreportable_long__all_'].astype(int) - df['change_in_nonreportable_short__all_'].astype(int)

        df['q_commercials'] = df['commercials_net_value'] / df['open_interest__all_']
        df['q_large_speculators'] = df['large_speculators_net_value'] / df['open_interest__all_']
        df['q_small_speculators'] = df['small_speculators_net_value'] / df['open_interest__all_']

        df['commercial_full_long_plus_short_position'] = df['commercial_positions_long__all_'] + df["commercial_positions_short__all_"]
        df['large_speculators_full_long_plus_short_position'] = df['noncommercial_positions_long__all_'] + df["noncommercial_positions_short__all_"]
        df['small_speculators_full_long_plus_short_position'] = df['nonreportable_positions_long__all_'] + df["nonreportable_positions_short__all_"]

        df['percent_commercials_long'] = df['commercial_positions_long__all_'] / df['commercial_full_long_plus_short_position']
        df['percent_commercials_short'] = df['commercial_positions_short__all_'] / df['commercial_full_long_plus_short_position']
        df['percent_large_speculators_long'] = df['noncommercial_positions_long__all_'] / df['large_speculators_full_long_plus_short_position']
        df['percent_large_speculators_short'] = df['noncommercial_positions_short__all_'] / df['large_speculators_full_long_plus_short_position']
        df['percent_small_speculators_long'] = df['nonreportable_positions_long__all_'] / df['small_speculators_full_long_plus_short_position']
        df['percent_small_speculators_short'] = df['nonreportable_positions_short__all_'] / df['small_speculators_full_long_plus_short_position']

        df['commercials_net_percent'] = df['percent_commercials_long'] - df['percent_commercials_short']
        df['large_speculators_net_percent'] = df['percent_large_speculators_long'] - df['percent_large_speculators_short']
        df['small_speculators_net_percent'] = df['percent_small_speculators_long'] - df['percent_small_speculators_short']

        df['min_q_c_0_5y'] = 0.0
        df['max_q_c_0_5y'] = 0.0
        df['min_q_nc_0_5y'] = 0.0
        df['max_q_nc_0_5y'] = 0.0
        df['min_q_nr_0_5y'] = 0.0
        df['max_q_nr_0_5y'] = 0.0

        df['min_q_c_1y'] = 0.0
        df['max_q_c_1y'] = 0.0
        df['min_q_nc_1y'] = 0.0
        df['max_q_nc_1y'] = 0.0
        df['min_q_nr_1y'] = 0.0
        df['max_q_nr_1y'] = 0.0

        df['min_q_c_2y'] = 0.0
        df['max_q_c_2y'] = 0.0
        df['min_q_nc_2y'] = 0.0
        df['max_q_nc_2y'] = 0.0
        df['min_q_nr_2y'] = 0.0
        df['max_q_nr_2y'] = 0.0

        df['min_q_c_3y'] = 0.0
        df['max_q_c_3y'] = 0.0
        df['min_q_nc_3y'] = 0.0
        df['max_q_nc_3y'] = 0.0
        df['min_q_nr_3y'] = 0.0
        df['max_q_nr_3y'] = 0.0

        df['min_q_c_4y'] = 0.0
        df['max_q_c_4y'] = 0.0
        df['min_q_nc_4y'] = 0.0
        df['max_q_nc_4y'] = 0.0
        df['min_q_nr_4y'] = 0.0
        df['max_q_nr_4y'] = 0.0

        df['min_q_c_5y'] = 0.0
        df['max_q_c_5y'] = 0.0
        df['min_q_nc_5y'] = 0.0
        df['max_q_nc_5y'] = 0.0
        df['min_q_nr_5y'] = 0.0
        df['max_q_nr_5y'] = 0.0

        df['c_index_0_5y'] = -1
        df['nc_index_0_5y'] = -1
        df['nr_index_0_5y'] = -1

        df['c_index_1y'] = -1
        df['nc_index_1y'] = -1
        df['nr_index_1y'] = -1

        df['c_index_2y'] = -1
        df['nc_index_2y'] = -1
        df['nr_index_2y'] = -1

        df['c_index_3y'] = -1
        df['nc_index_3y'] = -1
        df['nr_index_3y'] = -1

        df['c_index_4y'] = -1
        df['nc_index_4y'] = -1
        df['nr_index_4y'] = -1

        df['c_index_5y'] = -1
        df['nc_index_5y'] = -1
        df['nr_index_5y'] = -1


        connection = sqlite3.connect(self.db_path)
        df.to_sql('cot_table', connection, if_exists='replace', index=True, index_label='id')
        connection.commit()
        connection.close()

    def calculateWillCo(self, markets):
        for market in list(markets['contract_code']):
            self.calculateWillCoMinMax(market, 26)
            self.calculateWillCoMinMax(market, 52)
            self.calculateWillCoMinMax(market, 104)
            self.calculateWillCoMinMax(market, 156)
            self.calculateWillCoMinMax(market, 208)
            self.calculateWillCoMinMax(market, 260)

        self.calculateWillCoIndex(market)


    def calculateWillCoMinMax(self, market, weeks):
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        df = pd.read_sql_query("SELECT * FROM cot_table WHERE cftc_contract_market_code = ? ORDER BY id desc", connection, params=(market,))

        for i in range(len(df) - weeks + 1):
            print(i)

            c_min_val = df['q_commercials'].iloc[i:i + weeks].min()
            nc_min_val = df['q_large_speculators'].iloc[i:i + weeks].min()
            nr_min_val = df['q_small_speculators'].iloc[i:i + weeks].min()

            c_max_val = df['q_commercials'].iloc[i:i + weeks].max()
            nc_max_val = df['q_large_speculators'].iloc[i:i + weeks].max()
            nr_max_val = df['q_small_speculators'].iloc[i:i + weeks].max()

            if weeks == 26:
                df.at[i, 'min_q_c_0_5y'] = c_min_val
                df.at[i, 'min_q_nc_0_5y'] = nc_min_val
                df.at[i, 'min_q_nr_0_5y'] = nr_min_val
                df.at[i, 'max_q_c_0_5y'] = c_max_val
                df.at[i, 'max_q_nc_0_5y'] = nc_max_val
                df.at[i, 'max_q_nr_0_5y'] = nr_max_val
            elif weeks == 52:
                df.at[i, 'min_q_c_1y'] = c_min_val
                df.at[i, 'min_q_nc_1y'] = nc_min_val
                df.at[i, 'min_q_nr_1y'] = nr_min_val
                df.at[i, 'max_q_c_1y'] = c_max_val
                df.at[i, 'max_q_nc_1y'] = nc_max_val
                df.at[i, 'max_q_nr_1y'] = nr_max_val
            elif weeks == 104:
                df.at[i, 'min_q_c_2y'] = c_min_val
                df.at[i, 'min_q_nc_2y'] = nc_min_val
                df.at[i, 'min_q_nr_2y'] = nr_max_val
                df.at[i, 'max_q_c_2y'] = c_max_val
                df.at[i, 'max_q_nc_2y'] = nc_max_val
                df.at[i, 'max_q_nr_2y'] = nr_max_val
            elif weeks == 156:
                df.at[i, 'min_q_c_3y'] = c_min_val
                df.at[i, 'min_q_nc_3y'] = nc_min_val
                df.at[i, 'min_q_nr_3y'] = nr_min_val
                df.at[i, 'max_q_c_3y'] = c_max_val
                df.at[i, 'max_q_nc_3y'] = nc_max_val
                df.at[i, 'max_q_nr_3y'] = nr_max_val
            elif weeks == 208:
                df.at[i, 'min_q_c_4y'] = c_min_val
                df.at[i, 'min_q_nc_4y'] = nc_min_val
                df.at[i, 'min_q_nr_4y'] = nr_min_val
                df.at[i, 'max_q_c_4y'] = c_max_val
                df.at[i, 'max_q_nc_4y'] = nc_max_val
                df.at[i, 'max_q_nr_4y'] = nr_max_val
            elif weeks == 260:
                df.at[i, 'min_q_c_5y'] = c_min_val
                df.at[i, 'min_q_nc_5y'] = nc_min_val
                df.at[i, 'min_q_nr_5y'] = nr_min_val
                df.at[i, 'max_q_c_5y'] = c_max_val
                df.at[i, 'max_q_nc_5y'] = nc_max_val
                df.at[i, 'max_q_nr_5y'] = nr_max_val

            for i, row in df.iterrows():
                if weeks == 26:
                    cursor.execute("UPDATE cot_table SET min_q_c_0_5y = ? WHERE id = ?", (row['min_q_c_0_5y'], row['id']))
                    cursor.execute("UPDATE cot_table SET min_q_nc_0_5y = ? WHERE id = ?", (row['min_q_nc_0_5y'], row['id']))
                    cursor.execute("UPDATE cot_table SET min_q_nr_0_5y = ? WHERE id = ?", (row['min_q_nr_0_5y'], row['id']))
                    cursor.execute("UPDATE cot_table SET max_q_c_0_5y = ? WHERE id = ?", (row['max_q_c_0_5y'], row['id']))
                    cursor.execute("UPDATE cot_table SET max_q_nc_0_5y = ? WHERE id = ?", (row['max_q_nc_0_5y'], row['id']))
                    cursor.execute("UPDATE cot_table SET max_q_nr_0_5y = ? WHERE id = ?", (row['max_q_nr_0_5y'], row['id']))
                elif weeks == 52:
                    cursor.execute("UPDATE cot_table SET min_q_c_1y = ? WHERE id = ?", (row['min_q_c_1y'], row['id']))
                    cursor.execute("UPDATE cot_table SET min_q_nc_1y = ? WHERE id = ?", (row['min_q_nc_1y'], row['id']))
                    cursor.execute("UPDATE cot_table SET min_q_nr_1y = ? WHERE id = ?", (row['min_q_nr_1y'], row['id']))
                    cursor.execute("UPDATE cot_table SET max_q_c_1y = ? WHERE id = ?", (row['max_q_c_1y'], row['id']))
                    cursor.execute("UPDATE cot_table SET max_q_nc_1y = ? WHERE id = ?", (row['max_q_nc_1y'], row['id']))
                    cursor.execute("UPDATE cot_table SET max_q_nr_1y = ? WHERE id = ?", (row['max_q_nr_1y'], row['id']))
                elif weeks == 104:
                    cursor.execute("UPDATE cot_table SET min_q_c_2y = ? WHERE id = ?", (row['min_q_c_2y'], row['id']))
                    cursor.execute("UPDATE cot_table SET min_q_nc_2y = ? WHERE id = ?", (row['min_q_nc_2y'], row['id']))
                    cursor.execute("UPDATE cot_table SET min_q_nr_2y = ? WHERE id = ?", (row['min_q_nr_2y'], row['id']))
                    cursor.execute("UPDATE cot_table SET max_q_c_2y = ? WHERE id = ?", (row['max_q_c_2y'], row['id']))
                    cursor.execute("UPDATE cot_table SET max_q_nc_2y = ? WHERE id = ?", (row['max_q_nc_2y'], row['id']))
                    cursor.execute("UPDATE cot_table SET max_q_nr_2y = ? WHERE id = ?", (row['max_q_nr_2y'], row['id']))
                elif weeks == 156:
                    cursor.execute("UPDATE cot_table SET min_q_c_3y = ? WHERE id = ?", (row['min_q_c_3y'], row['id']))
                    cursor.execute("UPDATE cot_table SET min_q_nc_3y = ? WHERE id = ?", (row['min_q_nc_3y'], row['id']))
                    cursor.execute("UPDATE cot_table SET min_q_nr_3y = ? WHERE id = ?", (row['min_q_nr_3y'], row['id']))
                    cursor.execute("UPDATE cot_table SET max_q_c_3y = ? WHERE id = ?", (row['max_q_c_3y'], row['id']))
                    cursor.execute("UPDATE cot_table SET max_q_nc_3y = ? WHERE id = ?", (row['max_q_nc_3y'], row['id']))
                    cursor.execute("UPDATE cot_table SET max_q_nr_3y = ? WHERE id = ?", (row['max_q_nr_3y'], row['id']))
                elif weeks == 208:
                    cursor.execute("UPDATE cot_table SET min_q_c_4y = ? WHERE id = ?", (row['min_q_c_4y'], row['id']))
                    cursor.execute("UPDATE cot_table SET min_q_nc_4y = ? WHERE id = ?", (row['min_q_nc_4y'], row['id']))
                    cursor.execute("UPDATE cot_table SET min_q_nr_4y = ? WHERE id = ?", (row['min_q_nr_4y'], row['id']))
                    cursor.execute("UPDATE cot_table SET max_q_c_4y = ? WHERE id = ?", (row['max_q_c_4y'], row['id']))
                    cursor.execute("UPDATE cot_table SET max_q_nc_4y = ? WHERE id = ?", (row['max_q_nc_4y'], row['id']))
                    cursor.execute("UPDATE cot_table SET max_q_nr_4y = ? WHERE id = ?", (row['max_q_nr_4y'], row['id']))
                elif weeks == 260:
                    cursor.execute("UPDATE cot_table SET min_q_c_5y = ? WHERE id = ?", (row['min_q_c_5y'], row['id']))
                    cursor.execute("UPDATE cot_table SET min_q_nc_5y = ? WHERE id = ?", (row['min_q_nc_5y'], row['id']))
                    cursor.execute("UPDATE cot_table SET min_q_nr_5y = ? WHERE id = ?", (row['min_q_nr_5y'], row['id']))
                    cursor.execute("UPDATE cot_table SET max_q_c_5y = ? WHERE id = ?", (row['max_q_c_5y'], row['id']))
                    cursor.execute("UPDATE cot_table SET max_q_nc_5y = ? WHERE id = ?", (row['max_q_nc_5y'], row['id']))
                    cursor.execute("UPDATE cot_table SET max_q_nr_5y = ? WHERE id = ?", (row['max_q_nr_5y'], row['id']))
            
        connection.commit()
        connection.close()

    def calculateWillCoIndex(self, market):
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()

        df = pd.read_sql_query("SELECT * FROM cot_table WHERE cftc_contract_market_code = ? ORDER BY id desc", connection, params=(market,))
        rows = cursor.fetchall()

        q_c = rows[0]['q_commercials'];
        q_nc = rows[0]['q_large_speculators'];
        q_nr = rows[0]['q_small_speculators'];

        for row in rows:
            print(row)

            c_index_0_5y = round(((q_c - row["min_q_c_0_5y"]) / (row["max_q_c_0_5y"] - row["min_q_c_0_5y"])) * 100)
            nc_index_0_5y = round(((q_nc - row["min_q_nc_0_5y"]) / (row["max_q_nc_0_5y"] - row["min_q_nc_0_5y"])) * 100)
            nr_index_0_5y = round(((q_nr - row["min_q_nr_0_5y"]) / (row["max_q_nr_0_5y"] - row["min_nr_c_0_5y"])) * 100)

            c_index_1y = round(((q_c - row["min_q_c_1y"]) / (row["max_q_c_1y"] - row["min_q_c_1y"])) * 100)
            nc_index_1y = round(((q_nc - row["min_q_nc_1y"]) / (row["max_q_nc_1y"] - row["min_q_nc_1y"])) * 100)
            nr_index_1y = round(((q_nr - row["min_q_nr_1y"]) / (row["max_q_nr_1y"] - row["min_nr_c_1y"])) * 100)

            c_index_2y = round(((q_c - row["min_q_c_2y"]) / (row["max_q_c_2y"] - row["min_q_c_2y"])) * 100)
            nc_index_2y = round(((q_nc - row["min_q_nc_2y"]) / (row["max_q_nc_2y"] - row["min_q_nc_2y"])) * 100)
            nr_index_2y = round(((q_nr - row["min_q_nr_2y"]) / (row["max_q_nr_2y"] - row["min_nr_c_2y"])) * 100)

            c_index_3y = round(((q_c - row["min_q_c_3y"]) / (row["max_q_c_3y"] - row["min_q_c_3y"])) * 100)
            nc_index_3y = round(((q_nc - row["min_q_nc_3y"]) / (row["max_q_nc_3y"] - row["min_q_nc_3y"])) * 100)
            nr_index_3y = round(((q_nr - row["min_q_nr_3y"]) / (row["max_q_nr_3y"] - row["min_nr_c_3y"])) * 100)

            c_index_4y = round(((q_c - row["min_q_c_4y"]) / (row["max_q_c_4y"] - row["min_q_c_4y"])) * 100)
            nc_index_4y = round(((q_nc - row["min_q_nc_4y"]) / (row["max_q_nc_4y"] - row["min_q_nc_4y"])) * 100)
            nr_index_4y = round(((q_nr - row["min_q_nr_4y"]) / (row["max_q_nr_4y"] - row["min_nr_c_4y"])) * 100)

            c_index_5y = round(((q_c - row["min_q_c_5y"]) / (row["max_q_c_5y"] - row["min_q_c_5y"])) * 100)
            nc_index_5y = round(((q_nc - row["min_q_nc_5y"]) / (row["max_q_nc_5y"] - row["min_q_nc_5y"])) * 100)
            nr_index_5y = round(((q_nr - row["min_q_nr_5y"]) / (row["max_q_nr_5y"] - row["min_nr_c_5y"])) * 100)

            cursor.execute("UPDATE data_table SET c_index_0_5y = ? WHERE id = ?", (c_index_0_5y, row["id"]))
            cursor.execute("UPDATE data_table SET nc_index_0_5y = ? WHERE id = ?", (nc_index_0_5y, row["id"]))
            cursor.execute("UPDATE data_table SET nr_index_0_5y = ? WHERE id = ?", (nr_index_0_5y, row["id"]))

            cursor.execute("UPDATE data_table SET c_index_1y = ? WHERE id = ?", (c_index_1y, row["id"]))
            cursor.execute("UPDATE data_table SET nc_index_1y = ? WHERE id = ?", (nc_index_1y, row["id"]))
            cursor.execute("UPDATE data_table SET nr_index_1y = ? WHERE id = ?", (nr_index_1y, row["id"]))

            cursor.execute("UPDATE data_table SET c_index_2y = ? WHERE id = ?", (c_index_2y, row["id"]))
            cursor.execute("UPDATE data_table SET nc_index_2y = ? WHERE id = ?", (nc_index_2y, row["id"]))
            cursor.execute("UPDATE data_table SET nr_index_2y = ? WHERE id = ?", (nr_index_2y, row["id"]))

            cursor.execute("UPDATE data_table SET c_index_3y = ? WHERE id = ?", (c_index_3y, row["id"]))
            cursor.execute("UPDATE data_table SET nc_index_3y = ? WHERE id = ?", (nc_index_3y, row["id"]))
            cursor.execute("UPDATE data_table SET nr_index_3y = ? WHERE id = ?", (nr_index_3y, row["id"]))

            cursor.execute("UPDATE data_table SET c_index_4y = ? WHERE id = ?", (c_index_4y, row["id"]))
            cursor.execute("UPDATE data_table SET nc_index_4y = ? WHERE id = ?", (nc_index_4y, row["id"]))
            cursor.execute("UPDATE data_table SET nr_index_4y = ? WHERE id = ?", (nr_index_4y, row["id"]))

            cursor.execute("UPDATE data_table SET c_index_5y = ? WHERE id = ?", (c_index_5y, row["id"]))
            cursor.execute("UPDATE data_table SET nc_index_5y = ? WHERE id = ?", (nc_index_5y, row["id"]))
            cursor.execute("UPDATE data_table SET nr_index_5y = ? WHERE id = ?", (nr_index_5y, row["id"]))

        connection.commit()
        connection.close()
    
