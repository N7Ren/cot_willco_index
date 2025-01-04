import os
import pandas as pd
import argparse
import cot_reports as cot

def main(args):
    # Your main code logic here
    print(f"Running with arguments: {args}")

    markets = ['001601', '001602']
    df = cot.cot_hist(cot_report_type= 'legacy_fut')

    df2 = pd.DataFrame()
    begin_year = 2017
    end_year = 2025
    for i in reversed(range(begin_year, end_year)):
        single_year = pd.DataFrame(cot.cot_year(i, cot_report_type='legacy_fut')) 
        df2 = pd.concat([df2, single_year], ignore_index=True)

    for market in markets:
        csv_path = os.path.join(os.path.dirname(__file__), f"cot/cot_{market}.csv")
        asset = df[df['CFTC Contract Market Code'] == market].copy()
        asset.to_csv(csv_path, index=False)
    
        asset = df2[df2['CFTC Contract Market Code'] == market].copy()
        csv_path = os.path.join(os.path.dirname(__file__), f"cot/cot_{market}_2024_2017.csv")
        asset.to_csv(csv_path, index=False)

        print(f"Downloaded legacy_fut for market {market}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate CSVs for markets and WillCo.')
    parser.add_argument('--debug', action='store_true', help='Run the application in debug mode')
    args = parser.parse_args()
    
    if args.debug:
        print("Debug mode is on")
    
    main(args)