#!/usr/bin/env python3
"""
Debug the nested JSON parsing specifically
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.llm_fundamental_strategy import LLMFundamentalStrategy
import json

def test_nested_parsing():
    """Test nested JSON parsing specifically"""

    # Create strategy instance
    strategy = LLMFundamentalStrategy(name="Test LLM Strategy", params={})

    # Test the exact nested JSON case that's causing issues
    print("Testing nested JSON parsing...")

    # This simulates what we see in the database - a JSON string where the value field
    # contains another JSON string
    nested_json_string = '{"score": 0.65, "value": "{\\"score\\": 0.65, \\"value\\": \\"This is the actual analysis text.\\"}"}'

    print(f"Input: {nested_json_string}")

    try:
        # Parse the main JSON
        main_result = json.loads(nested_json_string)
        print(f"Main result: {main_result}")

        # Extract the value field
        value_field = main_result.get("value", "")
        print(f"Value field: {value_field}")
        print(f"Value field type: {type(value_field)}")

        # Try to parse the nested JSON in the value field
        if isinstance(value_field, str):
            try:
                nested_result = json.loads(value_field)
                print(f"Nested result: {nested_result}")
                print(f"Nested result type: {type(nested_result)}")

                if isinstance(nested_result, dict) and "value" in nested_result:
                    actual_value = nested_result.get("value", value_field)
                    print(f"Extracted actual value: {actual_value}")
                    print("+++ SUCCESS: Nested JSON parsing worked +++")
                else:
                    print("Nested result doesn't have 'value' key")

            except json.JSONDecodeError as e:
                print(f"Failed to parse nested JSON: {e}")

    except json.JSONDecodeError as e:
        print(f"Failed to parse main JSON: {e}")

if __name__ == "__main__":
    test_nested_parsing()

