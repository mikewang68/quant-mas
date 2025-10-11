#!/usr/bin/env python3
"""
Test script to verify if fundamental selector can correctly update pool records
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.llm_fundamental_strategy import LLMFundamentalStrategy
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def test_fundamental_selector_update_logic():
    """Test the fundamental selector update logic"""
    print("=== Testing Fundamental Selector Update Logic ===")

    # Create strategy instance
    strategy = LLMFundamentalStrategy(name="LLM基本面分析策略")

    # Test with a stock
    test_stock = "000985"  # 大庆华科

    print(f"\n1. Testing strategy execution for {test_stock}:")

    # Create mock stock_data
    stock_data = {test_stock: None}

    # Mock db_manager
    class MockDBManager:
        def __init__(self):
            self.db = {}

    db_manager = MockDBManager()

    selected_stocks = strategy.execute(stock_data, "test_agent", db_manager)

    if selected_stocks:
        first_stock = selected_stocks[0]
        print(f"  Strategy returned score: {first_stock.get('score')}")
        print(f"  Strategy returned value length: {len(first_stock.get('value', ''))}")

        # Check the value content
        try:
            import json
            parsed_value = json.loads(first_stock.get('value', ''))
            print(f"  Value JSON score: {parsed_value.get('score')}")
        except Exception as e:
            print(f"  Error parsing value: {e}")

    print(f"\n2. Simulating fundamental selector update logic:")

    # Simulate the update_latest_pool_record method logic
    fundamental_stocks = selected_stocks

    for fund_stock in fundamental_stocks:
        code = fund_stock.get('code')
        strategy_name = fund_stock.get('strategy_name', 'LLM基本面分析策略')
        score = fund_stock.get('score', 0.0)
        value = fund_stock.get('value', '')

        print(f"  Stock {code}:")
        print(f"    Strategy: {strategy_name}")
        print(f"    Raw score: {score}")
        print(f"    Value length: {len(value)}")

        # Simulate the score processing from fundamental_selector
        if score is not None:
            score_float = float(score)
            validated_score = max(0.0, min(1.0, score_float))
            rounded_score = round(validated_score, 2)
            print(f"    Processed score: {rounded_score}")
        else:
            rounded_score = 0.0
            print(f"    Processed score: {rounded_score} (default)")

        # Check what would be written to database
        fund_data = {
            'score': rounded_score,
            'value': value
        }

        print(f"    Would write to fund[{strategy_name}]: score={fund_data['score']}, value_length={len(fund_data['value'])}")

    print(f"\n3. Conclusion:")
    print(f"  The fundamental selector should write score: {rounded_score}")
    print(f"  The fundamental selector should write value: JSON string with score {parsed_value.get('score')}")
    print(f"  If database shows score=0.01, the issue is in the actual database update process")

if __name__ == "__main__":
    test_fundamental_selector_update_logic()

