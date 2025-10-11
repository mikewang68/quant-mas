#!/usr/bin/env python3
"""
Test script to display LLM fundamental analysis strategy output JSON content and format
"""

import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.llm_fundamental_strategy import LLMFundamentalStrategy
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def display_llm_output_format():
    """Display the format and content of LLM fundamental analysis strategy output"""
    print("=== LLM Fundamental Analysis Strategy Output Format ===")

    # Create strategy instance
    strategy = LLMFundamentalStrategy(name="LLM Fundamental Strategy")

    # Test with a stock
    test_stock = "000985"  # 大庆华科

    print(f"\n1. Testing stock: {test_stock}")

    # Test analyze_stock_fundamentals method
    print(f"\n2. Testing analyze_stock_fundamentals method:")

    analysis_result = strategy.analyze_stock_fundamentals(test_stock)

    print(f"Analysis result type: {type(analysis_result)}")
    print(f"Analysis result keys: {analysis_result.keys()}")

    print(f"\n3. Score field:")
    print(f"  score: {analysis_result['score']}")
    print(f"  score type: {type(analysis_result['score'])}")

    print(f"\n4. Value field (raw):")
    print(f"  value type: {type(analysis_result['value'])}")
    print(f"  value length: {len(analysis_result['value'])}")
    print(f"  value preview (first 500 chars):")
    print(f"  {analysis_result['value'][:500]}")

    print(f"\n5. Value field (parsed JSON):")
    try:
        parsed_value = json.loads(analysis_result['value'])
        print(f"  Parsed successfully!")
        print(f"  Parsed type: {type(parsed_value)}")
        print(f"  Parsed keys: {parsed_value.keys()}")

        print(f"\n6. Detailed JSON structure:")
        print(f"  score in parsed JSON: {parsed_value.get('score')}")
        print(f"  reason: {parsed_value.get('reason')}")
        print(f"  details keys: {list(parsed_value.get('details', {}).keys())}")
        print(f"  weights: {parsed_value.get('weights')}")
        print(f"  confidence_level: {parsed_value.get('confidence_level')}")
        print(f"  analysis_summary: {parsed_value.get('analysis_summary')}")
        print(f"  recommendation: {parsed_value.get('recommendation')}")
        print(f"  risk_factors: {parsed_value.get('risk_factors')}")
        print(f"  key_strengths: {parsed_value.get('key_strengths')}")

        print(f"\n7. Complete parsed JSON (formatted):")
        print(json.dumps(parsed_value, ensure_ascii=False, indent=2))

    except json.JSONDecodeError as e:
        print(f"  Failed to parse value as JSON: {e}")
        print(f"  Raw value content:")
        print(analysis_result['value'])

    # Test execute method
    print(f"\n8. Testing execute method output:")

    # Create mock stock_data
    stock_data = {test_stock: None}

    # Mock db_manager
    class MockDBManager:
        pass

    db_manager = MockDBManager()

    selected_stocks = strategy.execute(stock_data, "test_agent", db_manager)

    if selected_stocks:
        first_stock = selected_stocks[0]
        print(f"  Selected stock keys: {first_stock.keys()}")
        print(f"  code: {first_stock.get('code')}")
        print(f"  score: {first_stock.get('score')}")
        print(f"  selection_reason: {first_stock.get('selection_reason')}")
        print(f"  value type: {type(first_stock.get('value'))}")
        print(f"  value length: {len(first_stock.get('value', ''))}")

        # Try to parse the value field
        try:
            parsed_execute_value = json.loads(first_stock.get('value', ''))
            print(f"  Value parsed successfully!")
            print(f"  Parsed score: {parsed_execute_value.get('score')}")
        except json.JSONDecodeError as e:
            print(f"  Failed to parse execute value as JSON: {e}")

if __name__ == "__main__":
    display_llm_output_format()

