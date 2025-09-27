#!/usr/bin/env python3
"""
Debug script to check what data is returned by the LLM fundamental strategy
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.fundamental_selector import FundamentalStockSelector
from data.mongodb_manager import MongoDBManager
from utils.akshare_client import AkshareClient
import pandas as pd

def test_llm_strategy_execution():
    """Test what data the LLM strategy returns"""

    # Initialize components
    db_manager = MongoDBManager()
    data_fetcher = AkshareClient()

    # Create fundamental selector
    selector = FundamentalStockSelector(db_manager, data_fetcher)

    # Check what strategies were loaded
    print("Loaded strategies:")
    for i, strategy in enumerate(selector.strategy_instances):
        print(f"  {i}: {selector.strategy_names[i] if i < len(selector.strategy_names) else 'Unknown'}")

    # Check the first strategy instance
    if selector.strategy_instances:
        first_strategy = selector.strategy_instances[0]
        print(f"\nFirst strategy: {first_strategy.name}")
        print(f"Strategy class: {first_strategy.__class__.__name__}")

        # Get stock data for a specific stock (000061)
        print("\nGetting stock data for 000061...")
        stock_data = selector.get_standard_data(["000061"])

        if "000061" in stock_data:
            print(f"Got data for 000061: {len(stock_data['000061'])} records")

            # Execute the strategy directly
            print("\nExecuting strategy...")
            try:
                result = first_strategy.execute(stock_data, "基本面分析Agent", db_manager)
                print(f"Strategy execution result: {len(result)} items")

                # Print details of each result
                for i, item in enumerate(result):
                    print(f"\nItem {i}:")
                    print(f"  Code: {item.get('code')}")
                    print(f"  Score: {item.get('score')}")
                    print(f"  Value type: {type(item.get('value'))}")
                    value_str = str(item.get('value', ''))[:200]  # First 200 chars
                    print(f"  Value (first 200 chars): {value_str}")

                    # Check if value contains score
                    if str(item.get('score')) in value_str:
                        print("  *** WARNING: Score found in value field ***")

            except Exception as e:
                print(f"Error executing strategy: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("No data found for 000061")

if __name__ == "__main__":
    test_llm_strategy_execution()

