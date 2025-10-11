#!/usr/bin/env python3
"""
Test program for LLM Fundamental Strategy using qwen3-4B model
Outputs the complete JSON response from the large language model
"""

import os
import sys
import json
import logging

# Add project root to path for relative imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.llm_fundamental_strategy import LLMFundamentalStrategy

# Configure logging to see detailed output
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def main():
    print("=== LLM Fundamental Analysis Strategy Test with qwen3-4B ===\n")

    # Create LLM Fundamental Strategy instance with qwen3-4B configuration
    strategy_params = {
        "llm_config_name": "qwen3-4B"  # This matches the name in the database
    }

    strategy = LLMFundamentalStrategy(
        name="LLM基本面分析策略", params=strategy_params
    )

    # Test stock code
    stock_code = "300339"
    print(f"Analyzing stock {stock_code} using qwen3-4B model...")
    print(f"LLM Configuration: {strategy.llm_config.get('name', 'Unknown')}")
    print(f"API URL: {strategy.llm_config.get('api_url', 'Unknown')}")
    print(f"Model: {strategy.llm_config.get('model', 'Unknown')}")
    print(f"Provider: {strategy.llm_config.get('provider', 'Unknown')}")
    print()

    try:
        # Perform fundamental analysis
        result = strategy.analyze_stock_fundamentals(stock_code)

        # Output the complete JSON response from LLM
        print("\n=== LLM JSON Response ===")
        print("\nFull result structure:")
        print(json.dumps(result, indent=2, ensure_ascii=False))

        print("\n=== Detailed Analysis ===")
        print(f"Stock Code: {stock_code}")
        print(f"Score: {result.get('score', 'N/A')}")
        print(f"Value Type: {type(result.get('value', 'N/A'))}")

        # Check if value is a JSON string that can be parsed
        value_content = result.get('value', '')
        if isinstance(value_content, str):
            print(f"\nValue Content (first 500 chars):")
            print(value_content[:500] + "..." if len(value_content) > 500 else value_content)

            # Try to parse as JSON if it looks like JSON
            if value_content.strip().startswith('{') and value_content.strip().endswith('}'):
                try:
                    parsed_value = json.loads(value_content)
                    print("\nParsed Value Content:")
                    print(json.dumps(parsed_value, indent=2, ensure_ascii=False))
                except json.JSONDecodeError as e:
                    print(f"\nValue content is not valid JSON: {e}")
        else:
            print(f"\nValue Content: {value_content}")

        print("\n=== Strategy Execution Test ===")
        # Test the full strategy execution
        stock_data = {stock_code: None}  # Mock data for testing
        try:
            execution_results = strategy.execute(stock_data, "test_agent", None)
            print(f"Strategy execution completed. Results for {len(execution_results)} stocks:")
            for result in execution_results:
                print(f"  - {result['code']}: Score {result['score']}")
        except Exception as e:
            print(f"Strategy execution error: {e}")

    except Exception as e:
        print(f"Error analyzing stock {stock_code}: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

