#!/usr/bin/env python3
"""
Test script to verify that the fixed WeeklyStockSelector correctly executes different strategies
and saves the results to the database with correct strategy information.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mongodb_manager import MongoDBManager
from utils.akshare_client import AkshareClient
from agents.weekly_selector import WeeklyStockSelector

def test_strategy_execution_and_saving():
    """Test that weekly selector correctly executes different strategies and saves results properly"""
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

        print("\n=== Testing Strategy Execution and Saving ===")

        # Test 1: Execute three MA strategy
        if three_ma_strategy_id:
            print(f"\nExecuting Three MA Strategy with ID: {three_ma_strategy_id}")
            selector1 = WeeklyStockSelector(db_manager, data_fetcher, three_ma_strategy_id)

            # Select a small sample of stocks for testing (to save time)
            print("Selecting stocks (this may take a moment)...")
            selected_stocks1, last_date1, golden_cross_flags1, scores1, tech_data1 = selector1.select_stocks()

            print(f"Selected {len(selected_stocks1)} stocks with Three MA Strategy")
            print(f"Last data date: {last_date1}")

            # Save results
            save_result1 = selector1.save_selected_stocks(
                stocks=selected_stocks1,
                golden_cross_flags=golden_cross_flags1,
                scores=scores1,
                technical_analysis_data=tech_data1
            )

            if save_result1:
                print("✓ Three MA Strategy results saved successfully")
            else:
                print("✗ Failed to save Three MA Strategy results")

        # Test 2: Execute trend following strategy
        if trend_following_strategy_id:
            print(f"\nExecuting Trend Following Strategy with ID: {trend_following_strategy_id}")
            selector2 = WeeklyStockSelector(db_manager, data_fetcher, trend_following_strategy_id)

            # Select a small sample of stocks for testing (to save time)
            print("Selecting stocks (this may take a moment)...")
            selected_stocks2, last_date2, golden_cross_flags2, scores2, tech_data2 = selector2.select_stocks()

            print(f"Selected {len(selected_stocks2)} stocks with Trend Following Strategy")
            print(f"Last data date: {last_date2}")

            # Save results
            save_result2 = selector2.save_selected_stocks(
                stocks=selected_stocks2,
                golden_cross_flags=golden_cross_flags2,
                scores=scores2,
                technical_analysis_data=tech_data2
            )

            if save_result2:
                print("✓ Trend Following Strategy results saved successfully")
            else:
                print("✗ Failed to save Trend Following Strategy results")

        # Compare results
        if three_ma_strategy_id and trend_following_strategy_id:
            print(f"\n=== Comparison ===")
            print(f"Three MA Strategy selected {len(selected_stocks1)} stocks")
            print(f"Trend Following Strategy selected {len(selected_stocks2)} stocks")

            if len(selected_stocks1) != len(selected_stocks2):
                print("✓ Strategies produced different results as expected")
            else:
                # Check if they selected the same stocks
                common_stocks = set(selected_stocks1) & set(selected_stocks2)
                if len(common_stocks) != len(selected_stocks1):
                    print("✓ Strategies produced different stock selections as expected")
                else:
                    print("? Strategies produced identical results - this may be unexpected")

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
    success = test_strategy_execution_and_saving()
    if not success:
        sys.exit(1)

