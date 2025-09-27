#!/usr/bin/env python3
"""
Test script to check the actual LLM response handling
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.llm_fundamental_strategy import LLMFundamentalStrategy
import json

def test_llm_response_handling():
    """Test how the LLM response is handled"""

    # Create a strategy instance
    strategy = LLMFundamentalStrategy(name="Test LLM Strategy", params={})

    # Simulate an actual LLM response (based on what we saw in the test output)
    # This is a simplified version of what the LLM might return
    mock_response = '''{
        "score": 0.65,
        "value": "{\\"score\\": 0.65, \\"value\\": \\"This is the actual analysis text.\\"}"
    }'''

    print("Mock LLM response:")
    print(mock_response)

    # Test the get_llm_analysis method
    try:
        result = strategy.get_llm_analysis(mock_response)
        print("\nResult from get_llm_analysis:")
        print(f"Score: {result.get('score')}")
        print(f"Value: {result.get('value')}")
        print(f"Value type: {type(result.get('value'))}")
    except Exception as e:
        print(f"Error in get_llm_analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_llm_response_handling()

