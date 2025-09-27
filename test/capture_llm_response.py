#!/usr/bin/env python3
"""
Script to capture the actual LLM response for debugging
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Monkey patch the get_llm_analysis method to capture the actual response
from strategies.llm_fundamental_strategy import LLMFundamentalStrategy
import json

# Store the original method
original_get_llm_analysis = LLMFundamentalStrategy.get_llm_analysis

def patched_get_llm_analysis(self, prompt: str):
    """Patched version that captures the actual LLM response"""
    print("="*60)
    print("CAPTURING LLM RESPONSE")
    print("="*60)
    print(f"Prompt sent to LLM:\n{prompt[:200]}...")
    print("="*60)

    # Call the original method
    result = original_get_llm_analysis(self, prompt)

    print("Response received from LLM:")
    print(f"Result: {result}")
    print("="*60)

    return result

# Apply the patch
LLMFundamentalStrategy.get_llm_analysis = patched_get_llm_analysis

# Now run the fundamental selector
from agents.fundamental_selector import FundamentalStockSelector
from data.mongodb_manager import MongoDBManager
from utils.akshare_client import AkshareClient

def main():
    """Run the fundamental selector with patched LLM analysis"""
    print("Running fundamental selector with LLM response capture...")

    # Initialize components
    db_manager = MongoDBManager()
    data_fetcher = AkshareClient()

    # Create fundamental selector
    selector = FundamentalStockSelector(db_manager, data_fetcher)

    # Run the selector for stock 000061
    try:
        stock_data = selector.get_standard_data(["000061"])
        if selector.strategy_instances:
            first_strategy = selector.strategy_instances[0]
            print(f"Executing strategy: {first_strategy.name}")
            result = first_strategy.execute(stock_data, "基本面分析Agent", db_manager)
            print(f"Strategy result: {result}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

