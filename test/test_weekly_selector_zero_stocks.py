"""
Test script to verify weekly selector handles 0 stocks selection correctly
"""

import sys
import os
import pandas as pd
import numpy as np

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.weekly_selector import WeeklyStockSelector
from data.mongodb_manager import MongoDBManager


def test_zero_stocks_handling():
    """Test that weekly selector properly handles 0 stocks selection"""
    print("Testing weekly selector with 0 stocks selection...")

    try:
        # Initialize database manager
        db_manager = MongoDBManager()

        # Initialize weekly selector
        selector = WeeklyStockSelector(
            db_manager=db_manager
        )

        # Create test data that will result in 0 stocks selected
        # (e.g., stocks that don't meet any strategy criteria)
        stock_data = {}

        # Add some test stocks that won't meet selection criteria
        dates = pd.date_range("2023-01-01", periods=30, freq="D")

        # Create stocks with poor performance (low prices, low volume)
        for i in range(5):
            code = f"00000{i}"
            close_prices = np.array([
                5.0, 4.9, 4.8, 4.7, 4.6, 4.5, 4.4, 4.3, 4.2, 4.1,
                4.0, 3.9, 3.8, 3.7, 3.6, 3.5, 3.4, 3.3, 3.2, 3.1,
                3.0, 2.9, 2.8, 2.7, 2.6, 2.5, 2.4, 2.3, 2.2, 2.1
            ])
            volume_data = np.full(30, 100000)  # Low volume

            test_data = pd.DataFrame({
                'date': dates,
                'open': close_prices,
                'high': close_prices + 0.1,
                'low': close_prices - 0.1,
                'close': close_prices,
                'volume': volume_data
            })

            stock_data[code] = test_data

        # Execute selection
        strategy_results = selector.select_stocks(stock_data)

        print(f"Number of strategy results: {len(strategy_results)}")

        total_stocks_selected = 0
        for strategy_name, selected_stocks in strategy_results:
            print(f"Strategy '{strategy_name}': {len(selected_stocks)} stocks selected")
            total_stocks_selected += len(selected_stocks)

        print(f"Total stocks selected: {total_stocks_selected}")

        # Test saving 0 stocks to pool
        if total_stocks_selected == 0:
            print("\nTesting save_selected_stocks with 0 stocks...")

            # Use a test strategy ID and name
            strategy_id = "test_strategy"
            strategy_name = "Test Strategy"

            # Save 0 stocks
            success = selector.save_selected_stocks(
                strategy_results=strategy_results,
                strategy_id=strategy_id,
                strategy_name=strategy_name
            )

            print(f"Save operation successful: {success}")

            # Check if pool record was created/updated
            collection = db_manager.db["pool"]
            latest_record = collection.find_one(sort=[("_id", -1)])

            if latest_record:
                print(f"Latest pool record count: {latest_record.get('count', 'N/A')}")
                print(f"Latest pool record stocks: {len(latest_record.get('stocks', []))}")
                print(f"Strategy name in pool: {latest_record.get('strategy_name', 'N/A')}")
            else:
                print("No pool record found")

        print("\n" + "=" * 60)
        if total_stocks_selected == 0:
            print("✓ Test completed: Weekly selector correctly handled 0 stocks selection")
        else:
            print("✗ Test failed: Weekly selector selected stocks when none should be selected")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("=" * 60)
    print("Testing Weekly Selector Zero Stocks Handling")
    print("=" * 60)

    test_zero_stocks_handling()

