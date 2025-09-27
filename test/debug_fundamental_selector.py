#!/usr/bin/env python3
"""
Debug script to check what data is being passed to update_latest_pool_record
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.fundamental_selector import FundamentalStockSelector
from data.mongodb_manager import MongoDBManager
from utils.akshare_client import AkshareClient

def test_fundamental_selector_data():
    """Test what data the fundamental selector is processing"""

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

        # Check strategy parameters
        print(f"Strategy params: {getattr(first_strategy, 'params', 'No params')}")

if __name__ == "__main__":
    test_fundamental_selector_data()

