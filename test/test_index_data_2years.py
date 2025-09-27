#!/usr/bin/env python3
"""
Test script to verify 2-year index data fetching functionality
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from utils.akshare_client import AkshareClient
import pandas as pd
import datetime

def test_index_data_fetching():
    """Test fetching 2 years of index data"""
    print("Testing 2-year index data fetching...")

    # Initialize client
    client = AkshareClient()

    # Test indices
    test_indices = {
        '000016': '上证50',
        '000300': '沪深300',
        '000905': '中证500'
    }

    # Calculate date range (2 years)
    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days=2*365)

    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')

    print(f"Date range: {start_date_str} to {end_date_str}")
    print("="*60)

    # Test each index
    for code, name in test_indices.items():
        print(f"Testing {name} ({code})...")
        try:
            data = client.get_index_data(code, start_date_str, end_date_str)
            print(f"  Successfully retrieved {len(data)} records")

            if not data.empty:
                print(f"  Date range: {data['date'].min()} to {data['date'].max()}")
                print(f"  Close price range: {data['close'].min():.2f} to {data['close'].max():.2f}")
                print("  First 3 records:")
                print(data.head(3)[['date', 'open', 'close', 'volume']])
                print("  Last 3 records:")
                print(data.tail(3)[['date', 'open', 'close', 'volume']])
            else:
                print("  No data retrieved")

        except Exception as e:
            print(f"  Error: {e}")

        print("-" * 40)

    print("\nTest completed!")

if __name__ == "__main__":
    test_index_data_fetching()

