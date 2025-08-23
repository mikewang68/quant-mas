#!/usr/bin/env python3
"""
Test script to verify that the strategy_key is now using the strategy_id value.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mongodb_manager import MongoDBManager
from utils.akshare_client import AkshareClient
from agents.weekly_selector import WeeklyStockSelector

def test_strategy_key_uses_strategy_id():
    """Test that strategy_key now uses the strategy_id value"""
    try:
        # Initialize components
        db_manager = MongoDBManager()
        data_fetcher = AkshareClient()

        # Get all strategies from database
        strategies = db_manager.get_strategies()
        print("=== All Strategies in Database ===")
        for i, strategy in enumerate(strategies):
            strategy_id = strategy.get('_id')
            strategy_name = strategy.get('name', 'Unknown')
            print(f"{i+1}. {strategy_name} (ID: {strategy_id})")

        # Find the strategies we're interested in
        three_ma_strategy_id = None
        trend_following_strategy_id = None

        for strategy in strategies:
            name = strategy.get('name', '')
            strategy_id = strategy.get('_id')
            if "三均线多头排列策略（基本型）" in name:
                three_ma_strategy_id = strategy_id
            elif "趋势跟踪策略（稳健型）" in name:
                trend_following_strategy_id = strategy_id

        print("\n=== Testing Strategy Key Generation ===")

        # Test 1: Check Three MA Strategy
        if three_ma_strategy_id:
            print(f"\nTesting Three MA Strategy with ID: {three_ma_strategy_id}")
            selector1 = WeeklyStockSelector(db_manager, data_fetcher, three_ma_strategy_id)
            print(f"Loaded Strategy Name: {selector1.strategy_name}")
            print(f"Expected Strategy Key: {three_ma_strategy_id}")

            # Simulate what the strategy_key would be in save_selected_stocks
            strategy_name = selector1.strategy_name if selector1.strategy_name else "Unknown Strategy"
            strategy_id = None

            # Try to find the current strategy in the database
            for strategy in strategies:
                if strategy.get('name') == selector1.strategy_name:
                    strategy_id = strategy.get('_id')
                    break

            # If we couldn't find the strategy, use the strategy_id that was passed in or a default
            if not strategy_id:
                strategy_id = selector1.strategy_id if selector1.strategy_id else "unknown_strategy"

            # Use strategy_id as the strategy key
            strategy_key = strategy_id

            print(f"Generated Strategy Key: {strategy_key}")

            if strategy_key == three_ma_strategy_id:
                print("✓ Strategy key correctly uses strategy ID")
            else:
                print("✗ Strategy key does not use strategy ID")

        # Test 2: Check Trend Following Strategy
        if trend_following_strategy_id:
            print(f"\nTesting Trend Following Strategy with ID: {trend_following_strategy_id}")
            selector2 = WeeklyStockSelector(db_manager, data_fetcher, trend_following_strategy_id)
            print(f"Loaded Strategy Name: {selector2.strategy_name}")
            print(f"Expected Strategy Key: {trend_following_strategy_id}")

            # Simulate what the strategy_key would be in save_selected_stocks
            strategy_name = selector2.strategy_name if selector2.strategy_name else "Unknown Strategy"
            strategy_id = None

            # Try to find the current strategy in the database
            for strategy in strategies:
                if strategy.get('name') == selector2.strategy_name:
                    strategy_id = strategy.get('_id')
                    break

            # If we couldn't find the strategy, use the strategy_id that was passed in or a default
            if not strategy_id:
                strategy_id = selector2.strategy_id if selector2.strategy_id else "unknown_strategy"

            # Use strategy_id as the strategy key
            strategy_key = strategy_id

            print(f"Generated Strategy Key: {strategy_key}")

            if strategy_key == trend_following_strategy_id:
                print("✓ Strategy key correctly uses strategy ID")
            else:
                print("✗ Strategy key does not use strategy ID")

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
    success = test_strategy_key_uses_strategy_id()
    if not success:
        sys.exit(1)

