#!/usr/bin/env python3
"""
Test script to continue testing Weekly Selector functionality
Focuses on verifying the current implementation and identifying any issues
"""

import sys
import os
import logging

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data.mongodb_manager import MongoDBManager
from utils.akshare_client import AkshareClient
from agents.weekly_selector import WeeklyStockSelector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_weekly_selector_continuation():
    """Test weekly selector continuation - verify current implementation"""
    try:
        # Initialize components
        db_manager = MongoDBManager()
        data_fetcher = AkshareClient()

        # Get all strategies from database
        strategies = db_manager.get_strategies()
        print(f"Found {len(strategies)} strategies in database")

        if not strategies:
            print("No strategies found in database")
            return

        # Use first 2 strategies for testing
        strategy_ids = [str(strategies[0]["_id"]), str(strategies[1]["_id"])]
        print(f"Using strategy IDs: {strategy_ids}")

        # Initialize weekly selector with multiple strategies
        selector = WeeklyStockSelector(
            db_manager=db_manager,
            data_fetcher=data_fetcher,
            strategy_ids=strategy_ids
        )

        print(f"Loaded {len(selector.strategies)} strategies")

        # Test 1: Verify strategy loading
        for strategy_info in selector.strategies:
            print(f"Strategy: {strategy_info['name']}")
            print(f"  Class: {strategy_info['instance'].__class__.__name__}")
            print(f"  Params: {strategy_info['params']}")

        # Test 2: Verify data fetching
        print("\nTesting data fetching...")
        test_codes = ["000001", "000002"]  # Test with a few stocks
        stock_data = selector.get_standard_data(test_codes)
        print(f"Retrieved data for {len(stock_data)} stocks")

        for code, data in stock_data.items():
            print(f"  {code}: {len(data)} rows of data")

        # Test 3: Verify stock selection
        print("\nTesting stock selection...")
        strategy_results = selector.select_stocks()

        print(f"Strategy results type: {type(strategy_results)}")

        if isinstance(strategy_results, dict):
            print(f"Multiple strategies mode: {len(strategy_results)} strategies")
            for strategy_name, (selected_stocks, selection_reasons, scores, technical_analysis) in strategy_results.items():
                print(f"Strategy '{strategy_name}':")
                print(f"  Selected stocks: {len(selected_stocks)}")
                print(f"  Selection reasons type: {type(selection_reasons)}")
                print(f"  Scores type: {type(scores)}")
                print(f"  Technical analysis type: {type(technical_analysis)}")

                if selected_stocks:
                    # Show first 2 stocks with details
                    for i, stock in enumerate(selected_stocks[:2]):
                        print(f"    Stock {i+1}: {stock}")
                        if isinstance(selection_reasons, dict) and stock in selection_reasons:
                            print(f"      Reason: {selection_reasons[stock]}")
                        if isinstance(scores, dict) and stock in scores:
                            print(f"      Score: {scores[stock]}")
        else:
            print("Single strategy mode")

        # Test 4: Verify save functionality
        print("\nTesting save functionality...")
        if isinstance(strategy_results, dict):
            success = selector.save_selected_stocks(strategy_results)
            print(f"Save operation successful: {success}")
        else:
            print("Single strategy mode - skipping save test")

        # Test 5: Check pool data after save
        print("\nChecking pool data after save...")
        pool_data = db_manager.get_pool_data()
        if pool_data:
            latest_pool = db_manager.get_latest_pool_record()
            if latest_pool:
                print(f"Latest pool record strategy: {latest_pool.get('strategy_name', 'Unknown')}")
                stocks = latest_pool.get('stocks', [])
                print(f"Stocks in latest pool: {len(stocks)}")
                if stocks:
                    for stock in stocks[:3]:  # Show first 3 stocks
                        print(f"  Stock: {stock.get('code')}")
                        trend_data = stock.get('trend', {})
                        for strategy_name, strategy_data in trend_data.items():
                            print(f"    {strategy_name}: score={strategy_data.get('score', 'N/A')}")

        print("\n✓ All tests completed successfully!")

    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_weekly_selector_continuation()

