#!/usr/bin/env python3
"""
Test script to verify selection_reason is properly populated in strategy execution
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data.mongodb_manager import MongoDBManager
from utils.akshare_client import AkshareClient
from strategies.volume_breakout_strategy import VolumeBreakoutStrategy
import pandas as pd

def test_strategy_selection_reason():
    """Test that strategy properly returns selection_reason"""

    # Initialize components
    db_manager = MongoDBManager()
    data_fetcher = AkshareClient()

    # Create strategy instance with proper parameters
    strategy_params = {
        "volume_ratio_threshold": 1.5,
        "breakout_percentage": 0.02,
        "macd_positive_threshold": 0.0
    }
    strategy = VolumeBreakoutStrategy(strategy_params)

    # Test with a specific stock
    test_stock = "002083"

    print(f"Testing strategy execution for stock: {test_stock}")

    # Get stock data
    k_data = db_manager.get_k_data(test_stock)
    if k_data is None or k_data.empty:
        print(f"No data found for stock {test_stock}")
        return

    print(f"Got data for {test_stock}, shape: {k_data.shape}")

    # Execute strategy
    result = strategy.execute({test_stock: k_data}, "TestAgent", db_manager)

    print(f"\nStrategy execution result:")
    print(f"Type: {type(result)}")

    if isinstance(result, list):
        print(f"Number of results: {len(result)}")
        for i, stock_result in enumerate(result):
            print(f"\nResult {i+1}:")
            print(f"  Code: {stock_result.get('code')}")
            print(f"  Score: {stock_result.get('score')}")
            print(f"  Selection Reason: {stock_result.get('selection_reason')}")
            print(f"  Breakout Signal: {stock_result.get('breakout_signal')}")
            print(f"  Technical Analysis keys: {list(stock_result.get('technical_analysis', {}).keys())}")
    else:
        print(f"Unexpected result type: {result}")

if __name__ == "__main__":
    test_strategy_selection_reason()

