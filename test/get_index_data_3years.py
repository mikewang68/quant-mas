#!/usr/bin/env python3
"""
Script to fetch 3 years of data for 3 major Chinese indices using akshare
- 上证50 (SSE 50)
- 沪深300 (CSI 300)
- 中证500 (CSI 500)
"""

import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_index_data_3years():
    """
    Get 3 years of data for 3 major indices

    Returns:
        dict: Dictionary containing data for each index
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

    logger.info(f"Fetching data from {start_date_str} to {end_date_str}")

    # Fetch data for each index
    index_data = {}
    for code, name in indices.items():
        try:
            logger.info(f"Fetching data for {name} ({code})...")
            # Using index_zh_a_hist function as mentioned in the task
            data = ak.index_zh_a_hist(
                symbol=code,
                period="daily",
                start_date=start_date_str,
                end_date=end_date_str
            )

            # Store the data
            index_data[code] = {
                'name': name,
                'data': data
            }

            logger.info(f"Successfully fetched {len(data)} records for {name}")

        except Exception as e:
            logger.error(f"Error fetching data for {name} ({code}): {e}")
            index_data[code] = {
                'name': name,
                'data': pd.DataFrame()
            }

    return index_data

def display_index_data(index_data):
    """
    Display the index data in a formatted way

    Args:
        index_data (dict): Dictionary containing index data
    """
    print("\n" + "="*80)
    print("3 YEARS OF INDEX DATA FOR MAJOR CHINESE INDICES")
    print("="*80)

    for code, info in index_data.items():
        name = info['name']
        data = info['data']

        print(f"\n{name} ({code})")
        print("-" * 40)

        if data.empty:
            print("No data available")
            continue

        # Display basic information
        print(f"Total records: {len(data)}")

        if not data.empty:
            # Display first 5 rows
            print("\nFirst 5 records:")
            print(data.head().to_string(index=False))

            # Display last 5 rows
            print("\nLast 5 records:")
            print(data.tail().to_string(index=False))

            # Display some statistics
            if 'close' in data.columns:
                print(f"\nPrice statistics:")
                print(f"  Highest close: {data['close'].max():.2f}")
                print(f"  Lowest close: {data['close'].min():.2f}")
                print(f"  Latest close: {data['close'].iloc[-1]:.2f}")
                print(f"  First close: {data['close'].iloc[0]:.2f}")

def main():
    """
    Main function to execute the script
    """
    print("Fetching 3 years of data for major Chinese indices...")

    # Get the index data
    index_data = get_index_data_3years()

    # Display the data
    display_index_data(index_data)

    print("\n" + "="*80)
    print("DATA FETCHING COMPLETE")
    print("="*80)

if __name__ == "__main__":
    main()

