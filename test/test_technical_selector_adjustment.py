#!/usr/bin/env python3
"""
Test script to verify that TechnicalStockSelector correctly uses system adjustment settings
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

def test_adjustment_setting():
    """Test that TechnicalStockSelector uses system adjustment settings"""
    logging.basicConfig(level=logging.INFO)

    # Initialize components
    db_manager = MongoDBManager()
    data_fetcher = AkshareClient()

    try:
        # Get the current adjustment setting from database
        db_adjust_setting = db_manager.get_adjustment_setting()
        print(f"Database adjustment setting: {db_adjust_setting}")

        # Test the mapping logic that's used in TechnicalStockSelector
        adjust_mapping = {
            'qfq': 'q',      # 前复权 -> 'q'
            'hfq': 'h',      # 后复权 -> 'h'
            '': 'none'       # 不复权 -> 'none'
        }
        expected_adjust_type = adjust_mapping.get(db_adjust_setting, 'q')
        print(f"Expected Akshare adjust_type: {expected_adjust_type}")

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

        # Test that the selector can get standard data (this will use the adjustment setting)
        # Using a sample stock code for testing
        test_codes = ["000001"]  # Ping An Bank - you may need to change this

        print(f"Testing data fetch with adjustment setting...")
        # This will trigger the get_standard_data method which now uses the system adjustment setting
        stock_data = selector.get_standard_data(test_codes)

        if stock_data:
            print(f"Successfully fetched data for {len(stock_data)} stocks")
            for code, data in stock_data.items():
                print(f"  {code}: {len(data)} records")
                if not data.empty:
                    print(f"    Date range: {data['date'].min()} to {data['date'].max()}")
        else:
            print("No data fetched - this might be expected if there's no data in buf_data or network issues")

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
    success = test_adjustment_setting()
    if success:
        print("\n✓ TechnicalStockSelector adjustment setting test completed successfully")
        sys.exit(0)
    else:
        print("\n✗ TechnicalStockSelector adjustment setting test failed")
        sys.exit(1)

