#!/usr/bin/env python3
"""
Test script to debug the score inconsistency issue
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.llm_fundamental_strategy import LLMFundamentalStrategy
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def debug_score_inconsistency():
    """Debug why database score is 0.01 but value JSON shows 0.673"""
    print("=== Debugging Score Inconsistency ===")

    # Create strategy instance
    strategy = LLMFundamentalStrategy(name="Debug Strategy")

    # Test with a stock
    test_stock = "000985"  # 大庆华科

    print(f"\n1. Testing analyze_stock_fundamentals for {test_stock}:")

    analysis_result = strategy.analyze_stock_fundamentals(test_stock)

    print(f"  Raw analysis result score: {analysis_result['score']}")
    print(f"  Raw analysis result score type: {type(analysis_result['score'])}")

    # Test the score processing logic from fundamental_selector
    print(f"\n2. Testing score processing logic:")

    # Simulate the logic from fundamental_selector
    score = analysis_result.get('score', 0.0)
    print(f"  Original score from strategy: {score}")

    if score is not None:
        score_float = float(score)
        print(f"  After float conversion: {score_float}")

        # Ensure score is within valid range [0, 1]
        validated_score = max(0.0, min(1.0, score_float))
        print(f"  After validation: {validated_score}")

        rounded_score = round(validated_score, 2)
        print(f"  After rounding to 2 decimals: {rounded_score}")
    else:
        rounded_score = 0.0
        print(f"  Score is None, using default: {rounded_score}")

    print(f"\n3. Final score that would be written to database: {rounded_score}")

    # Check if there's any issue with the value field
    print(f"\n4. Checking value field:")
    try:
        import json
        parsed_value = json.loads(analysis_result['value'])
        print(f"  Score in value JSON: {parsed_value.get('score')}")
        print(f"  Score in value JSON type: {type(parsed_value.get('score'))}")
    except Exception as e:
        print(f"  Error parsing value JSON: {e}")

    # Test execute method
    print(f"\n5. Testing execute method:")

    # Create mock stock_data
    stock_data = {test_stock: None}

    # Mock db_manager
    class MockDBManager:
        pass

    db_manager = MockDBManager()

    selected_stocks = strategy.execute(stock_data, "test_agent", db_manager)

    if selected_stocks:
        first_stock = selected_stocks[0]
        print(f"  Execute method score: {first_stock.get('score')}")
        print(f"  Execute method score type: {type(first_stock.get('score'))}")

if __name__ == "__main__":
    debug_score_inconsistency()

