#!/usr/bin/env python3
"""
Debug script to check what scores are being generated for specific stocks
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.fundamental_selector import FundamentalStockSelector
from data.mongodb_manager import MongoDBManager
from utils.akshare_client import AkshareClient
from strategies.llm_fundamental_strategy import LLMFundamentalStrategy

def debug_stock_scores():
    """Debug scores for specific stocks"""

    # Initialize components
    db_manager = MongoDBManager()
    data_fetcher = AkshareClient()

    # Create fundamental selector
    selector = FundamentalStockSelector(db_manager, data_fetcher)

    # Check what strategies were loaded
    print("Loaded strategies:")
    for i, strategy in enumerate(selector.strategy_instances):
        print(f"  {i}: {selector.strategy_names[i] if i < len(selector.strategy_names) else 'Unknown'}")

    # Find LLM strategy
    llm_strategy = None
    for strategy in selector.strategy_instances:
        if isinstance(strategy, LLMFundamentalStrategy):
            llm_strategy = strategy
            break

    if not llm_strategy:
        print("No LLM strategy found!")
        return

    print(f"\nFound LLM strategy: {llm_strategy.name}")

    # Test specific stocks
    test_stocks = ["000828", "000833"]

    for stock_code in test_stocks:
        print(f"\n--- Testing stock {stock_code} ---")
        try:
            # Get stock data
            stock_data = selector.get_standard_data([stock_code])
            if not stock_data:
                print(f"No data found for {stock_code}")
                continue

            print(f"Got data for {stock_code}")

            # Execute LLM strategy
            results = llm_strategy.execute(stock_data, "基本面分析Agent", db_manager)
            print(f"Strategy execution results for {stock_code}:")
            for result in results:
                if result.get('code') == stock_code:
                    print(f"  Code: {result.get('code')}")
                    print(f"  Score: {result.get('score')}")
                    print(f"  Score type: {type(result.get('score'))}")
                    print(f"  Value: {result.get('value')[:100]}...")
                    break
            else:
                print(f"No result found for {stock_code}")

        except Exception as e:
            print(f"Error processing {stock_code}: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    debug_stock_scores()

