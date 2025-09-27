#!/usr/bin/env python3
"""
Script to fetch 3 years of data for 3 major Chinese indices using akshare's index_zh_a_hist function
- 上证50 (000016)
- 沪深300 (399300)
- 中证500 (000905)
"""

import akshare as ak
import pandas as pd
from datetime import datetime, timedelta

def fetch_index_data():
    """
    Fetch 3 years of data for 3 major indices using akshare's index_zh_a_hist function
    """
    # Define the indices we want to fetch
    indices = {
        '000016': '上证50',
        '399300': '沪深300',
        '000905': '中证500'
    }

    # Calculate date range (3 years)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=3*365)

    # Format dates for akshare (YYYYMMDD)
    start_date_str = start_date.strftime('%Y%m%d')
    end_date_str = end_date.strftime('%Y%m%d')

    print(f"Fetching data from {start_date_str} to {end_date_str}")
    print("="*60)

    # Fetch data for each index
    for code, name in indices.items():
        try:
            print(f"\nFetching data for {name} ({code})...")

            # Using akshare's index_zh_a_hist function as requested
            data = ak.index_zh_a_hist(
                symbol=code,
                period="daily",
                start_date=start_date_str,
                end_date=end_date_str
            )

            print(f"Successfully fetched {len(data)} records for {name}")

            # Display first 5 rows
            print(f"\nFirst 5 records for {name}:")
            print(data.head())

            # Display last 5 rows
            print(f"\nLast 5 records for {name}:")
            print(data.tail())

            # Display some statistics
            if not data.empty and 'close' in data.columns:
                print(f"\n{name} Statistics:")
                print(f"  Date range: {data['date'].min()} to {data['date'].max()}")
                print(f"  Closing price range: {data['close'].min():.2f} to {data['close'].max():.2f}")
                print(f"  Latest closing price: {data['close'].iloc[-1]:.2f}")
                print(f"  Average closing price: {data['close'].mean():.2f}")

        except Exception as e:
            print(f"Error fetching data for {name} ({code}): {e}")

    print("\n" + "="*60)
    print("Data fetching complete!")

if __name__ == "__main__":
    fetch_index_data()

