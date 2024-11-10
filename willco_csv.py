import os
import cot_reports as cot
import pandas as pd
import datetime

class WillCo:

    def __init__(self, csv_path):        
        self.csv_path = csv_path
        if not os.path.exists(self.csv_path):
            self.fetch_and_store_cot_data()

    def read_csv(self):
        return pd.read_csv(self.csv_path)

    def fetch_and_store_cot_data(self):
        df = pd.DataFrame()
        end_year = int(datetime.date.today().strftime('%Y')) + 1
        begin_year = end_year - 7
        for i in reversed(range(begin_year, end_year)):
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

        

        df.to_csv(self.csv_path, index=False)

    def calculateWillCo(self, df, market, weeks):
        asset = df[df['cftc_contract_market_code'] == market].copy()

        asset['lookback_(y)'] = "{:.1f}".format(weeks / 52)

        qCommercials = []
        qLargeSpeculators = []
        qSmallSpeculators = []

        for i in range(0, weeks + 1):
            try:
                qCommercials.append(asset.iloc[i]['q_commercials'])
            except IndexError:
                qCommercials.append(0)

            try:
                qLargeSpeculators.append(asset.iloc[i]['q_large_speculators'])
            except IndexError:
                qLargeSpeculators.append(0)
            
            try:
                qSmallSpeculators.append(asset.iloc[i]['q_small_speculators'])
            except IndexError:
                qSmallSpeculators.append(0)

        minQCommercialsNWeeks = min(qCommercials)
        maxQCommercialsNWeeks = max(qCommercials)

        minQLargeSpeculatorsNWeeks = min(qLargeSpeculators)
        maxQLargeSpeculatorsNWeeks = max(qLargeSpeculators)

        minQSmallpeculatorsNWeeks = min(qSmallSpeculators)
        maxQSmallpeculatorsNWeeks = max(qSmallSpeculators)

        asset['willco_commercials_index'] = round(((asset.iloc[0]['q_commercials'] - minQCommercialsNWeeks) / (maxQCommercialsNWeeks - minQCommercialsNWeeks)) * 100)
        asset['willco_large_specs_index'] = round(((asset.iloc[0]['q_large_speculators'] - minQLargeSpeculatorsNWeeks) / (maxQLargeSpeculatorsNWeeks - minQLargeSpeculatorsNWeeks)) * 100)
        asset['willco_small_specs_index'] = round(((asset.iloc[0]['q_small_speculators'] - minQSmallpeculatorsNWeeks) / (maxQSmallpeculatorsNWeeks - minQSmallpeculatorsNWeeks)) * 100)

        if weeks == 26:
            asset['commercials_net_(%)'] = (asset.iloc[0]['commercials_net_percent'].round(2) * 100).astype(int)
            asset['large_speculators_net_(%)'] = (asset.iloc[0]['large_speculators_net_percent'].round(2) * 100).astype(int)
            asset['small_speculators_net_(%)'] = (asset.iloc[0]['small_speculators_net_percent'].round(2) * 100).astype(int)

            asset['commercials_change_(%)'] = ((asset.iloc[0]['percent_commercials_long'] - asset.iloc[1]['percent_commercials_long']).round(2) * 100).astype(int)
            asset['large_speculators_change_(%)'] = ((asset.iloc[0]['percent_large_speculators_long'] - asset.iloc[1]['percent_large_speculators_long']).round(2) * 100).astype(int)
            asset['small_speculators_change_(%)'] = ((asset.iloc[0]['percent_small_speculators_long'] - asset.iloc[1]['percent_small_speculators_long']).round(2) * 100).astype(int)
        else:
            asset['commercials_net_(%)'] = 0
            asset['large_speculators_net_(%)'] = 0
            asset['small_speculators_net_(%)'] = 0

            asset['commercials_change_(%)'] = 0
            asset['large_speculators_change_(%)'] = 0
            asset['small_speculators_change_(%)'] = 0


        return asset.head(1)[['market_and_exchange_names', 'lookback_(y)', 
                              'willco_commercials_index', 'willco_large_specs_index', 'willco_small_specs_index', 
                              'commercials_change_(%)', 'large_speculators_change_(%)', 'small_speculators_change_(%)',
                              'commercials_net_(%)', 'large_speculators_net_(%)', 'small_speculators_net_(%)', 'as_of_date_in_form_yyyy_mm_dd']]
    
