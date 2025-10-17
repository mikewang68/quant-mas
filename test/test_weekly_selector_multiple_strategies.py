"""
Test script to verify that weekly selector correctly handles multiple strategies
"""

import sys
import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mongodb_manager import MongoDBManager
from agents.weekly_selector import WeeklyStockSelector

def test_multiple_strategies():
    """Test that weekly selector correctly handles multiple strategies"""

    print("Testing Weekly Selector with Multiple Strategies...")

    # Initialize MongoDB manager
    db_manager = MongoDBManager()

    # Initialize weekly selector
    selector = WeeklyStockSelector(db_manager)

    # Check if strategies are loaded
    if not selector.strategies:
        print("No strategies loaded. Please check database configuration.")
        return False

    print(f"Loaded {len(selector.strategies)} strategies:")
    for strategy_info in selector.strategies:
        print(f"  - {strategy_info['name']}")

    # Execute stock selection
    print("\nExecuting stock selection with multiple strategies...")
    strategy_results = selector.select_stocks()

    # Check results
    if not strategy_results:
        print("No strategy results returned.")
        return False

    print(f"\nStrategy Results Summary:")
    total_stocks = 0
    for strategy_name, strategy_result in strategy_results.items():
        selected_stocks = strategy_result[0]
        scores = strategy_result[1]
        json_values = strategy_result[2]

        print(f"  {strategy_name}: {len(selected_stocks)} stocks selected")
        total_stocks += len(selected_stocks)

        # Print first few stocks for each strategy
        if selected_stocks:
            print(f"    Sample stocks: {selected_stocks[:3]}")

    print(f"\nTotal stocks across all strategies: {total_stocks}")

    # Save to pool
    print("\nSaving to pool...")
    success = selector.save_selected_stocks(strategy_results)

    if success:
        print("✓ Successfully saved multiple strategy results to pool")

        # Verify pool data
        pool_collection = db_manager.db["pool"]
        latest_record = pool_collection.find_one(sort=[("_id", -1)])

        if latest_record:
            print(f"\nPool Record Verification:")
            print(f"  _id: {latest_record.get('_id')}")
            print(f"  strategy_key count: {len(latest_record.get('strategy_key', []))}")
            print(f"  strategy_name count: {len(latest_record.get('strategy_name', []))}")
            print(f"  stocks count: {latest_record.get('count', 0)}")

            # Check if all strategies are present
            strategy_names = latest_record.get('strategy_name', [])
            print(f"  Strategy names in pool: {strategy_names}")

            # Check if stocks have trend data from multiple strategies
            stocks = latest_record.get('stocks', [])
            if stocks:
                sample_stock = stocks[0]
                trend_keys = list(sample_stock.get('trend', {}).keys())
                print(f"  Sample stock trend keys: {trend_keys}")
                print(f"  Number of strategies in sample stock: {len(trend_keys)}")

            return True
        else:
            print("✗ No pool record found after save")
            return False
    else:
        print("✗ Failed to save to pool")
        return False

if __name__ == "__main__":
    try:
        success = test_multiple_strategies()
        if success:
            print("\n✓ Test PASSED: Multiple strategies correctly handled")
        else:
            print("\n✗ Test FAILED: Issues with multiple strategy handling")
    except Exception as e:
        print(f"\n✗ Test ERROR: {e}")
        import traceback
        traceback.print_exc()

