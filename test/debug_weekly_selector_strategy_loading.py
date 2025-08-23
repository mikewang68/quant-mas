#!/usr/bin/env python3
"""
Test script to verify the issues with weekly selector strategy loading and execution
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mongodb_manager import MongoDBManager
from utils.akshare_client import AkshareClient
from agents.weekly_selector import WeeklyStockSelector

def test_strategy_loading():
    """Test that weekly selector loads the correct strategy"""
    try:
        # Initialize components
        db_manager = MongoDBManager()
        data_fetcher = AkshareClient()

        # Get all strategies from database
        strategies = db_manager.get_strategies()
        print("=== All Strategies in Database ===")
        for i, strategy in enumerate(strategies):
            print(f"{i+1}. {strategy.get('name', 'Unknown')} (ID: {strategy.get('_id')})")
            if 'program' in strategy:
                print(f"   Program: {strategy['program']}")
            print(f"   Parameters: {strategy.get('parameters', {})}")
            print()

        # Find the two strategies we're interested in
        three_ma_strategy = None
        trend_following_strategy = None

        for strategy in strategies:
            name = strategy.get('name', '')
            if "三均线多头排列策略（基本型）" in name:
                three_ma_strategy = strategy
            elif "趋势跟踪策略（稳健型）" in name:
                trend_following_strategy = strategy

        print("=== Testing Strategy Loading ===")

        # Test 1: Load three MA strategy
        if three_ma_strategy:
            print(f"Testing Three MA Strategy: {three_ma_strategy.get('name')}")
            # Temporarily modify the database to make this the first strategy
            # (In real implementation, we'd modify the weekly selector to load the correct strategy)

        # Test 2: Load trend following strategy
        if trend_following_strategy:
            print(f"Testing Trend Following Strategy: {trend_following_strategy.get('name')}")

        # Test 3: Check WeeklySelector behavior
        print("\n=== Testing WeeklySelector Strategy Loading ===")
        selector = WeeklyStockSelector(db_manager, data_fetcher)
        print(f"Loaded Strategy Name: {selector.strategy_name}")
        print(f"Loaded Strategy File: {selector.strategy_file}")
        print(f"Loaded Strategy Class: {selector.strategy_class_name}")
        print(f"Loaded Strategy Parameters: {selector.strategy_params}")

        # Check if it matches what we expect
        first_strategy = strategies[0] if strategies else None
        if first_strategy:
            expected_name = first_strategy.get('name', 'Unknown')
            print(f"First Strategy in DB: {expected_name}")
            if selector.strategy_name == expected_name:
                print("✓ WeeklySelector correctly loads the first strategy")
            else:
                print("✗ WeeklySelector does NOT load the first strategy")

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

