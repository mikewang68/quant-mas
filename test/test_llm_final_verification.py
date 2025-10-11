#!/usr/bin/env python3
"""
Final verification test for LLM Fundamental Strategy with qwen3-4B
Tests the actual JSON output format from the strategy
"""

import os
import sys
import json

# Add project root to path for relative imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.llm_fundamental_strategy import LLMFundamentalStrategy


def main():
    print("=== Final LLM Fundamental Strategy Verification ===\n")

    # Create LLM Fundamental Strategy instance with qwen3-4B configuration
    strategy_params = {
        "llm_config_name": "qwen3-4B"
    }

    strategy = LLMFundamentalStrategy(
        name="LLM基本面分析策略", params=strategy_params
    )

    # Test stock code
    stock_code = "300339"
    print(f"Testing stock {stock_code} with qwen3-4B model...")
    print(f"LLM Configuration: {strategy.llm_config}")
    print()

    try:
        # Perform fundamental analysis
        print("=== Performing Fundamental Analysis ===")
        result = strategy.analyze_stock_fundamentals(stock_code)

        # Output the complete result
        print("\n=== Analysis Result ===")
        print(f"Score: {result.get('score', 'N/A')}")
        print(f"Value Type: {type(result.get('value', 'N/A'))}")

        # Check if value is JSON string
        value_content = result.get('value', '')
        if isinstance(value_content, str):
            print(f"\nValue Content Length: {len(value_content)} characters")

            # Try to parse as JSON
            try:
                parsed_value = json.loads(value_content)
                print("✅ Value is valid JSON")
                print("\n=== Parsed Value Content ===")
                print(json.dumps(parsed_value, indent=2, ensure_ascii=False))

                # Check for required fields in the parsed JSON
                required_fields = ["score", "reason", "details", "weights", "confidence_level",
                                 "analysis_summary", "recommendation", "risk_factors", "key_strengths"]
                missing_fields = [field for field in required_fields if field not in parsed_value]

                if missing_fields:
                    print(f"\n⚠️  Missing required fields: {missing_fields}")
                else:
                    print("\n✅ All required fields present in value JSON")

            except json.JSONDecodeError:
                print("❌ Value is not valid JSON")
                print(f"\nValue Content Preview (first 500 chars):")
                print(value_content[:500] + "..." if len(value_content) > 500 else value_content)

        print("\n=== Strategy Execution Test ===")
        # Test the full strategy execution
        stock_data = {stock_code: None}
        execution_results = strategy.execute(stock_data, "test_agent", None)

        print(f"Strategy execution completed. Results for {len(execution_results)} stocks:")
        for result in execution_results:
            print(f"  - {result['code']}: Score {result['score']}")

            # Check if the value field contains the expected JSON structure
            value_str = result.get('value', '')
            if isinstance(value_str, str):
                try:
                    parsed_value = json.loads(value_str)
                    print(f"    ✅ Value is valid JSON with {len(parsed_value)} fields")
                except json.JSONDecodeError:
                    print(f"    ❌ Value is not valid JSON")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

