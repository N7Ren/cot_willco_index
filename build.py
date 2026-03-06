import os
import json
import pandas as pd
from datetime import datetime
from willco import WillCo

DEFAULT_LOW = 10
DEFAULT_HIGH = 90

def load_markets():
    csv_path = os.path.join(os.path.dirname(__file__), "markets.csv")
    try:
        df = pd.read_csv(csv_path, dtype=str)
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        print(f"Error loading markets.csv: {e}")
        return pd.DataFrame()

def build_static_site():
    print("Starting static build...")
    
    csv_path = os.path.join(os.path.dirname(__file__), "cot.csv")
    will_co = WillCo(csv_path)
    
    # Load markets
    markets_df = load_markets()
    if markets_df.empty:
        return

    # Load raw data
    print("Checking for new COT data...")
    will_co.fetch_and_store_cot_data()
    csv_df = will_co.read_csv()
    
    # Calculate all periods for all markets
    all_results = []
    market_codes = markets_df['contract_code'].tolist()
    
    print(f"Calculating data for {len(market_codes)} markets...")

    # Bolt Optimization: Pre-group data by market code to avoid repeated full-dataframe filtering inside loops.
    # This turns O(N*M) filtering into O(N) grouping + O(1) lookups.
    grouped_csv_df = {market: group for market, group in csv_df.groupby('cftc_contract_market_code')}

    for market in market_codes:
        if market not in grouped_csv_df:
            continue
        market_df = grouped_csv_df[market]
        for weeks in [26, 52, 104, 156, 208, 260]:
            df = will_co.calculateWillCo(market_df, market, weeks)
            if not df.empty:
                # Add weeks as an explicit column for the frontend
                row = df.iloc[0].to_dict()
                row['weeks'] = weeks
                # Bolt Optimization: Append standard Python dicts to a list instead of creating/concat single-row DataFrames
                all_results.append(row)
    
    if not all_results:
        print("No data calculated!")
        return

    results_df = pd.DataFrame(all_results)
    
    # Convert to JSON-friendly format
    # We'll use records format (list of dicts)
    data_list = results_df.to_dict(orient='records')
    
    # Prepare metadata
    metadata = {
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "default_low": DEFAULT_LOW,
        "default_high": DEFAULT_HIGH,
        "markets": markets_df['contract_name'].tolist()
    }
    
    output = {
        "metadata": metadata,
        "data": data_list
    }
    
    # Write to data.json
    with open("data.json", "w") as f:
        json.dump(output, f)
    
    print(f"Successfully exported {len(data_list)} rows to data.json")

if __name__ == "__main__":
    build_static_site()
