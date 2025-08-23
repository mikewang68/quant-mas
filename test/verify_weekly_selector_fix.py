#!/usr/bin/env python3
"""
Test script to verify that WeeklyStockSelector can now load the correct strategy
based on the provided strategy ID.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mongodb_manager import MongoDBManager
from utils.akshare_client import AkshareClient
from agents.weekly_selector import WeeklyStockSelector

def test_strategy_loading_with_id():
    """Test that weekly selector loads the correct strategy when given a strategy ID"""
    try:
        # Initialize components
        db_manager = MongoDBManager()
        data_fetcher = AkshareClient()

        # Get all strategies from database
        strategies = db_manager.get_strategies()
        print("=== All Strategies in Database ===")
        strategy_map = {}
        for i, strategy in enumerate(strategies):
            strategy_id = strategy.get('_id')
            strategy_name = strategy.get('name', 'Unknown')
            strategy_map[strategy_id] = strategy_name
            print(f"{i+1}. {strategy_name} (ID: {strategy_id})")

        # Find the two strategies we're interested in
        three_ma_strategy_id = None
        trend_following_strategy_id = None

        for strategy in strategies:
            name = strategy.get('name', '')
            strategy_id = strategy.get('_id')
            if "三均线多头排列策略（基本型）" in name:
                three_ma_strategy_id = strategy_id
            elif "趋势跟踪策略（稳健型）" in name:
                trend_following_strategy_id = strategy_id

        print("\n=== Testing Strategy Loading with Specific IDs ===")

        # Test 1: Load three MA strategy with specific ID
        if three_ma_strategy_id:
            print(f"\nTesting Three MA Strategy with ID: {three_ma_strategy_id}")
            selector1 = WeeklyStockSelector(db_manager, data_fetcher, three_ma_strategy_id)
            print(f"Loaded Strategy Name: {selector1.strategy_name}")
            print(f"Loaded Strategy File: {selector1.strategy_file}")
            print(f"Loaded Strategy Class: {selector1.strategy_class_name}")
            print(f"Loaded Strategy Parameters: {selector1.strategy_params}")

            if "三均线多头排列策略" in selector1.strategy_name:
                print("✓ Correctly loaded Three MA Strategy")
            else:
                print("✗ Failed to load Three MA Strategy")

        # Test 2: Load trend following strategy with specific ID
        if trend_following_strategy_id:
            print(f"\nTesting Trend Following Strategy with ID: {trend_following_strategy_id}")
            selector2 = WeeklyStockSelector(db_manager, data_fetcher, trend_following_strategy_id)
            print(f"Loaded Strategy Name: {selector2.strategy_name}")
            print(f"Loaded Strategy File: {selector2.strategy_file}")
            print(f"Loaded Strategy Class: {selector2.strategy_class_name}")
            print(f"Loaded Strategy Parameters: {selector2.strategy_params}")

            if "趋势跟踪策略" in selector2.strategy_name:
                print("✓ Correctly loaded Trend Following Strategy")
            else:
                print("✗ Failed to load Trend Following Strategy")

        # Test 3: Load without specifying ID (should load first strategy)
        print(f"\nTesting Default Loading (should load first strategy)")
        selector3 = WeeklyStockSelector(db_manager, data_fetcher)
        print(f"Loaded Strategy Name: {selector3.strategy_name}")

        first_strategy_name = strategies[0].get('name', 'Unknown') if strategies else 'None'
        print(f"First Strategy in DB: {first_strategy_name}")

        if selector3.strategy_name == first_strategy_name:
            print("✓ Correctly loaded first strategy by default")
        else:
            print("✗ Failed to load first strategy by default")

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
    success = test_strategy_loading_with_id()
    if not success:
        sys.exit(1)

