#!/usr/bin/env python3
"""
Test script to verify that strategy parameters are correctly saved to the pool
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mongodb_manager import MongoDBManager
from data.database_operations import DatabaseOperations
from datetime import datetime

def test_strategy_parameters_saving():
    """Test that strategy parameters are correctly saved to pool"""
    print("Testing strategy parameters saving...")

    # Initialize database manager and operations
    db_manager = MongoDBManager()
    db_ops = DatabaseOperations(db_manager)

    # Find the actual strategy
    strategies = db_manager.get_strategies()
    strategy_id = None
    strategy_name = None
    for strategy in strategies:
        if strategy.get('name') == '三均线多头排列策略（基本型）':
            strategy_id = strategy.get('_id')
            strategy_name = strategy.get('name')
            strategy_params = strategy.get('parameters', {})
            print(f"Found strategy: {strategy_name}")
            print(f"Strategy ID: {strategy_id}")
            print(f"Strategy parameters: {strategy_params}")
            break

    if not strategy_id:
        print("Error: Could not find the 三均线多头排列策略（基本型） strategy")
        return False

    # Test data
    test_stocks = [
        {'code': '000001', 'reason': 'Test stock 1', 'score': 0.8},
        {'code': '000002', 'reason': 'Test stock 2', 'score': 0.7}
    ]

    # Save to pool with None for strategy_params to let the method fetch from DB
    result = db_ops.save_selected_stocks_to_pool(
        strategy_key="test_weekly_selector",
        agent_name="TestSelector",
        strategy_id=strategy_id,
        strategy_name=strategy_name,
        stocks=test_stocks,
        date=datetime.now().strftime('%Y-%m-%d'),
        strategy_params=None  # This should trigger fetching from database
    )

    if result:
        print("Successfully saved to pool")

        # Check the saved record
        pool_collection = db_manager.db['pool']
        latest_record = pool_collection.find_one(sort=[('updated_at', -1)])
        if latest_record:
            saved_params = latest_record.get('strategy_parameters', {})
            print(f"Saved strategy parameters: {saved_params}")

            # Verify that parameters were saved
            if saved_params and len(saved_params) > 0:
                print("SUCCESS: Strategy parameters were correctly saved!")
                return True
            else:
                print("ERROR: Strategy parameters are still empty")
                return False
        else:
            print("ERROR: No pool record found")
            return False
    else:
        print("ERROR: Failed to save to pool")
        return False

if __name__ == "__main__":
    try:
        success = test_strategy_parameters_saving()
        if success:
            print("\nTest completed successfully!")
        else:
            print("\nTest failed!")
            sys.exit(1)
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

