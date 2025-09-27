#!/usr/bin/env python3
"""
Test to verify the LLM parsing behavior
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.llm_fundamental_strategy import LLMFundamentalStrategy
import json

def test_llm_parsing():
    """Test LLM parsing with a response that should fail"""

    # Create strategy instance
    strategy = LLMFundamentalStrategy(name="Test LLM Strategy", params={})

    # Simulate a response with invalid JSON (control characters)
    invalid_json_response = '''{
    "score": 0.65,
    "value": "This is a test with\ninvalid control characters"
}'''

    print("Testing invalid JSON response:")
    print(invalid_json_response)

    try:
        result = strategy.get_llm_analysis(invalid_json_response)
        print(f"Result: {result}")
        print(f"Score: {result.get('score')}")
        print(f"Value: {result.get('value')}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_llm_parsing()

