"""
Test script for Weekly Selector functionality
"""

import sys
import os
import logging

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data.mongodb_manager import MongoDBManager
from agents.weekly_selector import WeeklyStockSelector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_weekly_selector():
    """Test the Weekly Selector functionality"""

    try:
        # Initialize components
        db_manager = MongoDBManager()

        # Create Weekly Selector instance
        weekly_selector = WeeklyStockSelector(db_manager)

        print("=== Testing Weekly Selector ===")
        print(f"Loaded strategy: {weekly_selector.strategy_name}")
        print(f"Number of strategies: {len(weekly_selector.strategies)}")

        # Test stock selection
        selected_stocks, last_data_date, golden_cross_flags, scores, technical_analysis_data, strategy_results = weekly_selector.select_stocks()

        print(f"\n=== Selection Results ===")
        print(f"Selected stocks: {len(selected_stocks)}")
        print(f"Last data date: {last_data_date}")

        if selected_stocks:
            print(f"First 10 selected stocks: {selected_stocks[:10]}")

            # Save results to pool
            save_result = weekly_selector.save_selected_stocks(
                stocks=selected_stocks,
                golden_cross_flags=golden_cross_flags,
                scores=scores,
                technical_analysis_data=technical_analysis_data,
                strategy_results=strategy_results
            )

            print(f"Save to pool successful: {save_result}")
        else:
            print("No stocks selected - this might be normal if no stocks meet the criteria")

        return True

    except Exception as e:
        print(f"Error testing Weekly Selector: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_weekly_selector()
    if success:
        print("\n✅ Weekly Selector test completed successfully")
    else:
        print("\n❌ Weekly Selector test failed")

