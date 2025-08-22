#!/usr/bin/env python3
"""
Debug script to test weekly selector parameter loading
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Mock the database manager to avoid connection issues
class MockDBManager:
    def get_strategies(self):
        # Return the actual strategy from database
        return [{
            "_id": "68a6591d8dace06d7edd9582",
            "name": "三均线多头排列策略（基本型）",
            "type": "technical",
            "description": "使用斐波那契数列设置3均线，分别是5,13,34,均线多头排列",
            "parameters": {
                "ma_long": "34",
                "ma_mid": "13",
                "ma_short": "5"
            },
            "program": {
                "file": "three_ma_bullish_arrangement_strategy",
                "class": "ThreeMABullishArrangementStrategy"
            },
            "created_at": "2025-08-15",
            "class_name": "ThreeMABullishArrangementStrategy",
            "file": "three_ma_bullish_arrangement_strategy"
        }]

# Mock the data fetcher
class MockDataFetcher:
    pass

def test_weekly_selector_loading():
    """Test how weekly selector loads and processes strategy parameters"""
    print("Testing weekly selector parameter loading...")

    # Import after setting up mocks
    from agents.weekly_selector import WeeklyStockSelector

    # Create instances
    db_manager = MockDBManager()
    data_fetcher = MockDataFetcher()

    # Create selector
    selector = WeeklyStockSelector(db_manager, data_fetcher)

    # Check loaded parameters
    print(f"Strategy name: {selector.strategy_name}")
    print(f"Strategy file: {selector.strategy_file}")
    print(f"Strategy class name: {selector.strategy_class_name}")
    print(f"Strategy params: {selector.strategy_params}")

    # Check if strategy instance was created
    if selector.strategy_instance:
        print(f"Strategy instance created: {selector.strategy_instance}")
        print(f"Strategy instance params: {getattr(selector.strategy_instance, 'params', 'No params attribute')}")
    else:
        print("No strategy instance created")

if __name__ == "__main__":
    test_weekly_selector_loading()

