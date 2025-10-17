#!/usr/bin/env python3
"""
Test script to verify the fix for weekly selector with multiple strategies
"""

import sys
import os
import logging

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data.mongodb_manager import MongoDBManager
from utils.akshare_client import AkshareClient
from agents.weekly_selector import WeeklyStockSelector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_weekly_selector_multiple_strategies():
    """Test weekly selector with multiple strategies"""
    try:
        # Initialize components
        db_manager = MongoDBManager()
        data_fetcher = AkshareClient()

        # Get all strategies from database
        strategies = db_manager.get_strategies()
        print(f"Found {len(strategies)} strategies in database")

        # Filter for weekly selector strategies (you can adjust this filter)
        weekly_strategies = [strategy for strategy in strategies if "趋势" in strategy.get("name", "")]
        print(f"Using {len(weekly_strategies)} weekly strategies")

        if not weekly_strategies:
            print("No weekly strategies found, using all strategies")
            weekly_strategies = strategies[:2]  # Use first 2 strategies for testing

        # Get strategy IDs
        strategy_ids = [str(strategy["_id"]) for strategy in weekly_strategies]
        print(f"Strategy IDs: {strategy_ids}")

        # Initialize weekly selector with multiple strategies
        selector = WeeklyStockSelector(
            db_manager=db_manager,
            data_fetcher=data_fetcher,
            strategy_ids=strategy_ids
        )

        print(f"Loaded {len(selector.strategies)} strategies")

        # Select stocks
        print("Selecting stocks...")
        strategy_results = selector.select_stocks()

        print(f"Strategy results type: {type(strategy_results)}")

        if isinstance(strategy_results, dict):
            print(f"Multiple strategies mode: {len(strategy_results)} strategies")
            for strategy_name, (selected_stocks, selection_reasons, scores, technical_analysis) in strategy_results.items():
                print(f"Strategy '{strategy_name}': {len(selected_stocks)} stocks selected")
                if selected_stocks:
                    print(f"  Selected stocks: {selected_stocks[:3]}")  # Show first 3
                    print(f"  Selection reasons type: {type(selection_reasons)}")
                    print(f"  Scores type: {type(scores)}")
                    print(f"  Technical analysis type: {type(technical_analysis)}")
        else:
            print("Single strategy mode")
            print(f"Selected stocks: {strategy_results[0]}")

        # Save selected stocks
        print("\nSaving selected stocks to database...")
        if isinstance(strategy_results, dict):
            success = selector.save_selected_stocks(strategy_results)
            print(f"Save operation successful: {success}")
        else:
            print("Single strategy mode - skipping save test")

        print("\nTest completed successfully!")

    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_weekly_selector_multiple_strategies()

