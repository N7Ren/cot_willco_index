import time
import pandas as pd
import numpy as np
from willco import WillCo
import os

def run_benchmark():
    csv_path = "cot.csv"
    if not os.path.exists(csv_path):
        print("Fetching COT data...")
        w = WillCo(csv_path)

    w = WillCo(csv_path)
    df = w.read_csv()

    # Get some markets to test with
    markets = df['cftc_contract_market_code'].unique()[:10]
    weeks_list = [26, 52, 104, 156, 208, 260]

    start_time = time.time()
    iterations = 100
    for _ in range(iterations):
        for market in markets:
            for weeks in weeks_list:
                w.calculateWillCo(df, market, weeks)
    end_time = time.time()

    avg_time = (end_time - start_time) / iterations
    print(f"Average time per full set of calculations: {avg_time:.4f} seconds")

if __name__ == "__main__":
    run_benchmark()
