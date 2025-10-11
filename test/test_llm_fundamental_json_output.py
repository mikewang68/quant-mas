#!/usr/bin/env python3
"""
Enhanced test program for LLM Fundamental Strategy using qwen3-4B model
Specifically designed to capture and display the complete JSON response from LLM
"""

import os
import sys
import json
import logging
import requests

# Add project root to path for relative imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.llm_fundamental_strategy import LLMFundamentalStrategy

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def test_llm_response_directly():
    """Test LLM API directly to see the raw response format"""
    print("\n=== Testing LLM API Directly ===")

    # Load LLM configuration from database
    strategy = LLMFundamentalStrategy(
        name="LLM基本面分析策略",
        params={"llm_config_name": "qwen3-4B"}
    )

    # Create a simple test prompt
    test_prompt = {
        "role": "user",
        "content": "请输出一个简单的JSON格式：{\"score\": 0.75, \"value\": \"测试分析内容\"}"
    }

    try:
        # Call LLM directly
        result = strategy.get_llm_analysis(test_prompt)
        print("\nDirect LLM API Test Result:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Direct API test failed: {e}")


def main():
    print("=== Enhanced LLM Fundamental Analysis Strategy Test ===")
    print("Testing with qwen3-4B model to capture complete JSON response\n")

    # Create LLM Fundamental Strategy instance with qwen3-4B configuration
    strategy_params = {
        "llm_config_name": "qwen3-4B"
    }

    strategy = LLMFundamentalStrategy(
        name="LLM基本面分析策略", params=strategy_params
    )

    # Test stock code
    stock_code = "300339"
    print(f"Analyzing stock {stock_code} using qwen3-4B model...")
    print(f"LLM Configuration: {strategy.llm_config}")
    print()

    try:
        # Perform fundamental analysis
        print("\n=== Starting Fundamental Analysis ===")
        result = strategy.analyze_stock_fundamentals(stock_code)

        # Output the complete JSON response from LLM
        print("\n=== Complete LLM JSON Response ===")
        print("\nFull result structure:")
        print(json.dumps(result, indent=2, ensure_ascii=False))

        print("\n=== Detailed Response Analysis ===")
        print(f"Stock Code: {stock_code}")
        print(f"Score: {result.get('score', 'N/A')}")
        print(f"Score Type: {type(result.get('score', 'N/A'))}")
        print(f"Value Type: {type(result.get('value', 'N/A'))}")

        # Detailed analysis of the value field
        value_content = result.get('value', '')
        print(f"\nValue Content Length: {len(value_content)} characters")

        if isinstance(value_content, str):
            print(f"\nValue Content Preview (first 1000 chars):")
            print(value_content[:1000] + "..." if len(value_content) > 1000 else value_content)

            # Check if value contains JSON
            if value_content.strip().startswith('{') and value_content.strip().endswith('}'):
                print("\nValue appears to be JSON format, attempting to parse...")
                try:
                    parsed_value = json.loads(value_content)
                    print("Successfully parsed value as JSON:")
                    print(json.dumps(parsed_value, indent=2, ensure_ascii=False))
                except json.JSONDecodeError as e:
                    print(f"Failed to parse value as JSON: {e}")
                    print("Value content may contain invalid JSON or mixed content")
            else:
                print("\nValue does not appear to be JSON format")

                # Check for common patterns in the response
                if '<think>' in value_content.lower():
                    print("\n⚠️  WARNING: Response contains <think> tags")
                if '首先' in value_content:
                    print("\n⚠️  WARNING: Response contains Chinese thinking patterns")
                if 'json' in value_content.lower():
                    print("\n⚠️  WARNING: Response may contain JSON code blocks")

        print("\n=== Strategy Execution Results ===")
        # Test the full strategy execution
        stock_data = {stock_code: None}  # Mock data for testing
        try:
            execution_results = strategy.execute(stock_data, "test_agent", None)
            print(f"Strategy execution completed. Results for {len(execution_results)} stocks:")
            for result in execution_results:
                print(f"  - {result['code']}: Score {result['score']}")
                print(f"    Value preview: {str(result['value'])[:200]}...")
        except Exception as e:
            print(f"Strategy execution error: {e}")
            import traceback
            traceback.print_exc()

    except Exception as e:
        print(f"Error analyzing stock {stock_code}: {e}")
        import traceback
        traceback.print_exc()

    # Test direct LLM API call
    test_llm_response_directly()


if __name__ == "__main__":
    main()

