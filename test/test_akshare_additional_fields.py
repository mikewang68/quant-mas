#!/usr/bin/env python3
"""
Test script to verify that AkshareClient returns additional financial metrics
"""

import sys
import os
import logging
from datetime import datetime, timedelta

# Add the project root to the path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from utils.akshare_client import AkshareClient

def test_akshare_additional_fields():
    """Test that AkshareClient returns additional financial metrics"""
    logging.basicConfig(level=logging.INFO)

    # Initialize Akshare client
    client = AkshareClient()

    try:
        # Get a sample stock code
        print("Getting stock list...")
        codes = client.get_stock_list()

        if not codes:
            print("No stock codes found")
            return False

        test_code = codes[0]  # Use the first stock code
        print(f"Testing with stock code: {test_code}")

        # Get daily K-data with additional fields
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

        print(f"Getting daily K-data for {test_code} from {start_date} to {end_date}...")
        k_data = client.get_daily_k_data(test_code, start_date, end_date, "q")  # 前复权

        if k_data.empty:
            print("No data returned")
            return False

        print(f"Data shape: {k_data.shape}")
        print("Columns:", list(k_data.columns))
        print("\nFirst few rows:")
        print(k_data.head())

        # Check if additional fields are present
        expected_fields = ['amplitude', 'pct_change', 'change_amount', 'turnover_rate']
        missing_fields = [field for field in expected_fields if field not in k_data.columns]

        if missing_fields:
            print(f"Missing fields: {missing_fields}")
            return False
        else:
            print("All expected fields are present")

        # Check if the fields have non-zero values
        print("\nChecking field values:")
        for field in expected_fields:
            non_zero_count = (k_data[field] != 0).sum()
            print(f"  {field}: {non_zero_count} non-zero values out of {len(k_data)}")

            if non_zero_count > 0:
                print(f"    Sample values: {k_data[field].head().tolist()}")

        print("\nTest completed successfully!")
        return True

    except Exception as e:
        print(f"Error in test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_akshare_additional_fields()
    if success:
        print("\n✓ AkshareClient additional fields test completed successfully")
        sys.exit(0)
    else:
        print("\n✗ AkshareClient additional fields test failed")
        sys.exit(1)

