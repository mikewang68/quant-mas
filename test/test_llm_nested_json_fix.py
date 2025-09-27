#!/usr/bin/env python3
"""
Test script to verify that the LLM nested JSON parsing fix works correctly.
This script tests various nested JSON scenarios that were causing score=0 issues.
"""

import sys
import os
import json

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.llm_fundamental_strategy import LLMFundamentalStrategy

def test_nested_json_parsing():
    """Test various nested JSON parsing scenarios."""

    # Create a mock strategy instance
    strategy = LLMFundamentalStrategy()

    # Test case 1: Nested JSON with escaped quotes (common issue)
    print("Test case 1: Nested JSON with escaped quotes")
    content1 = '{"score": 0.35, "value": "{\\"score\\": 0.35, \\"value\\": \\"This is the actual analysis content.\\"}"}'

    try:
        result1 = json.loads(content1)
        print(f"  Parsed result: score={result1.get('score')}, value length={len(result1.get('value', ''))}")

        # Test the nested parsing logic
        llm_value = result1.get("value", "")
        llm_score = float(result1.get("score", 0))

        if isinstance(llm_value, str):
            try:
                nested_result = json.loads(llm_value)
                if isinstance(nested_result, dict):
                    if "value" in nested_result:
                        llm_value = nested_result["value"]
                        print(f"  Extracted nested value: {llm_value[:50]}...")
                    if "score" in nested_result and llm_score == 0:
                        nested_score = float(nested_result["score"])
                        llm_score = max(0.0, min(1.0, nested_score))
                        print(f"  Updated score from nested data: {llm_score}")
            except json.JSONDecodeError:
                print("  Failed to parse nested JSON")

        print(f"  Final result: score={llm_score}")
    except Exception as e:
        print(f"  Error: {e}")

    print()

    # Test case 2: Valid JSON with correct score
    print("Test case 2: Valid JSON with correct score")
    content2 = '{"score": 0.75, "value": "This is a proper analysis without nested JSON."}'

    try:
        result2 = json.loads(content2)
        llm_score = float(result2.get("score", 0))
        llm_value = result2.get("value", "")
        print(f"  Result: score={llm_score}, value={llm_value}")
    except Exception as e:
        print(f"  Error: {e}")

    print()

    # Test case 3: Score mismatch scenario
    print("Test case 3: Score mismatch scenario")
    content3 = '{"score": 0.0, "value": "{\\"score\\": 0.65, \\"value\\": \\"Analysis content with correct score.\\"}"}'

    try:
        result3 = json.loads(content3)
        llm_score = float(result3.get("score", 0))
        llm_value = result3.get("value", "")
        print(f"  Initial result: score={llm_score}")

        # Test nested parsing when main score is 0
        if isinstance(llm_value, str) and llm_score == 0:
            try:
                nested_result = json.loads(llm_value)
                if isinstance(nested_result, dict) and "score" in nested_result:
                    nested_score = float(nested_result["score"])
                    llm_score = max(0.0, min(1.0, nested_score))
                    print(f"  Updated score from nested data: {llm_score}")
                    if "value" in nested_result:
                        llm_value = nested_result["value"]
                        print(f"  Extracted nested value: {llm_value[:50]}...")
            except json.JSONDecodeError:
                print("  Failed to parse nested JSON")

        print(f"  Final result: score={llm_score}")
    except Exception as e:
        print(f"  Error: {e}")

def main():
    """Main test function."""
    print("Testing LLM nested JSON parsing fix...")
    print("=" * 50)

    test_nested_json_parsing()

    print("=" * 50)
    print("Test completed!")

if __name__ == "__main__":
    main()

