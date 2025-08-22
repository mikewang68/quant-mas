#!/usr/bin/env python3
"""
Test script to verify that WeeklyStockSelector correctly loads strategy information
from the program field in the database.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.weekly_selector import WeeklyStockSelector
from data.mongodb_manager import MongoDBManager
from utils.akshare_client import AkshareClient

def test_strategy_loading():
    """Test that WeeklyStockSelector correctly loads strategy information"""
    try:
        # Initialize components
        db_manager = MongoDBManager()
        data_fetcher = AkshareClient()

        # Create a test strategy with program field
        test_strategy = {
            "name": "Test Strategy with Program Field",
            "type": "technical",
            "description": "Test strategy to verify program field handling",
            "program": {
                "file": "test_strategy_file",
                "class": "TestStrategyClass"
            },
            "parameters": {"test_param": "test_value"}
        }

        # Save test strategy to database
        strategy_id = db_manager.create_strategy(test_strategy)
        print(f"Created test strategy with ID: {strategy_id}")

        if not strategy_id:
            print("Failed to create test strategy")
            return False

        # Initialize WeeklyStockSelector
        selector = WeeklyStockSelector(db_manager, data_fetcher)

        # Load strategy from database
        selector._load_strategy_from_db()

        # Check that strategy information was loaded correctly
        print(f"Strategy name: {selector.strategy_name}")
        print(f"Strategy file: {selector.strategy_file}")
        print(f"Strategy class name: {selector.strategy_class_name}")
        print(f"Strategy parameters: {selector.strategy_params}")

        # Verify the values
        if selector.strategy_name != "Test Strategy with Program Field":
            print("Strategy name not loaded correctly")
            return False

        if selector.strategy_file != "test_strategy_file":
            print("Strategy file not loaded correctly from program field")
            return False

        if selector.strategy_class_name != "TestStrategyClass":
            print("Strategy class name not loaded correctly from program field")
            return False

        if selector.strategy_params.get("test_param") != "test_value":
            print("Strategy parameters not loaded correctly")
            return False

        print("All tests passed! Strategy information loaded correctly from program field.")

        # Cleanup
        db_manager.delete_strategy(strategy_id)

        return True

    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        try:
            db_manager.close_connection()
        except:
            pass

if __name__ == "__main__":
    success = test_strategy_loading()
    if not success:
        sys.exit(1)

