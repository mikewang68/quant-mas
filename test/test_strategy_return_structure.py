#!/usr/bin/env python3
"""
Test script to check strategy return data structure
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.llm_fundamental_strategy import LLMFundamentalStrategy
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def test_strategy_return_structure():
    """Test the structure of strategy return data"""
    print("=== Testing Strategy Return Data Structure ===")

    # Create strategy instance
    strategy = LLMFundamentalStrategy(name="Test Strategy")

    # Test with a stock
    test_stock = "000985"  # 大庆华科

    # Get financial data
    financial_data = strategy.get_financial_data(test_stock)

    # Test analyze_stock_fundamentals method
    print(f"\n1. Testing analyze_stock_fundamentals for {test_stock}")

    analysis_result = strategy.analyze_stock_fundamentals(test_stock)
    print(f"Analysis result type: {type(analysis_result)}")
    print(f"Analysis result keys: {analysis_result.keys()}")
    print(f"Analysis result: {analysis_result}")

    # Test execute method
    print(f"\n2. Testing execute method for {test_stock}")

    # Create mock stock_data
    stock_data = {test_stock: None}  # Just need the key for testing

    # Mock db_manager
    class MockDBManager:
        pass

    db_manager = MockDBManager()

    selected_stocks = strategy.execute(stock_data, "test_agent", db_manager)
    print(f"Selected stocks type: {type(selected_stocks)}")
    print(f"Selected stocks length: {len(selected_stocks)}")
    if selected_stocks:
        print(f"First stock data: {selected_stocks[0]}")
        print(f"First stock keys: {selected_stocks[0].keys()}")

if __name__ == "__main__":
    test_strategy_return_structure()

