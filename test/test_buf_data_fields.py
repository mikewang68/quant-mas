#!/usr/bin/env python3
"""
Test script to verify that TechnicalStockSelector saves additional financial metrics to buf_data
"""

import sys
import os
import logging

# Add the project root to the path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from data.mongodb_manager import MongoDBManager
from utils.akshare_client import AkshareClient
from agents.technical_selector import TechnicalStockSelector

def test_buf_data_fields():
    """Test that TechnicalStockSelector saves additional financial metrics to buf_data"""
    logging.basicConfig(level=logging.INFO)

    # Initialize components
    db_manager = MongoDBManager()
    data_fetcher = AkshareClient()

    try:
        # Initialize TechnicalStockSelector
        selector = TechnicalStockSelector(
            db_manager=db_manager,
            data_fetcher=data_fetcher,
            name="TestTechnicalSelector"
        )

        print("TechnicalStockSelector initialized successfully")
        print(f"Loaded {len(selector.strategy_names)} strategies:")
        for i, strategy_name in enumerate(selector.strategy_names):
            print(f"  {i+1}. {strategy_name}")

        # Test with a sample stock code
        test_codes = ["000001"]  # Ping An Bank - you may need to change this

        print(f"Testing data fetch and buf_data save...")
        # This will trigger the get_standard_data method which fetches data and saves to buf_data
        stock_data = selector.get_standard_data(test_codes)

        if stock_data:
            print(f"Successfully fetched data for {len(stock_data)} stocks")
            for code, data in stock_data.items():
                print(f"  {code}: {len(data)} records")
                if not data.empty:
                    print(f"    Date range: {data['date'].min()} to {data['date'].max()}")

                    # Check if additional fields are present in the fetched data
                    expected_fields = ['amplitude', 'pct_change', 'change_amount', 'turnover_rate']
                    missing_fields = [field for field in expected_fields if field not in data.columns]

                    if missing_fields:
                        print(f"    Missing fields in fetched data: {missing_fields}")
                    else:
                        print(f"    All expected fields present in fetched data")

                        # Show sample values
                        print(f"    Sample values:")
                        for field in expected_fields:
                            if len(data) > 0:
                                sample_value = data[field].iloc[0]
                                print(f"      {field}: {sample_value}")
        else:
            print("No data fetched")

        # Now check if the data was saved correctly to buf_data with additional fields
        print(f"\nChecking buf_data records...")
        buf_data_collection = db_manager.db["buf_data"]

        # Get a few records for the test stock
        buf_records = list(buf_data_collection.find({"code": "000001"}).limit(3))

        if buf_records:
            print(f"Found {len(buf_records)} buf_data records for 000001")
            for i, record in enumerate(buf_records):
                print(f"  Record {i+1}:")
                print(f"    Date: {record.get('date')}")
                print(f"    Code: {record.get('code')}")

                # Check for additional fields
                expected_fields = ['amplitude', 'pct_change', 'change_amount', 'turnover_rate']
                for field in expected_fields:
                    value = record.get(field, "MISSING")
                    print(f"    {field}: {value}")
        else:
            print("No buf_data records found for 000001")

        print("Test completed successfully!")
        return True

    except Exception as e:
        print(f"Error in test: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Clean up
        if 'db_manager' in locals():
            db_manager.close_connection()

if __name__ == "__main__":
    success = test_buf_data_fields()
    if success:
        print("\n✓ TechnicalStockSelector buf_data fields test completed successfully")
        sys.exit(0)
    else:
        print("\n✗ TechnicalStockSelector buf_data fields test failed")
        sys.exit(1)

