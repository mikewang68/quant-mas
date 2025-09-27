#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple test to demonstrate LLM error handling logic
"""

import json

def test_json_parsing_success():
    """Test successful JSON parsing"""
    # This is what we expect from a well-behaved LLM
    good_response = '{"score": 0.85, "value": "This stock has strong fundamentals."}'

    try:
        result = json.loads(good_response)
        score = result.get("score", 0.0)
        value = result.get("value", "")
        print(f"✓ Success case - Score: {score}, Value: {value}")
    except json.JSONDecodeError:
        print("✗ Success case failed - This should not happen!")

def test_json_parsing_failure():
    """Test JSON parsing failure handling"""
    # This is what happens when LLM response is malformed
    bad_response = '{"score": 0.85, "value": "This stock has strong fundamentals."\\x00\\x01}'

    try:
        result = json.loads(bad_response)
        score = result.get("score", 0.0)
        value = result.get("value", "")
        print(f"✓ This should work - Score: {score}, Value: {value}")
    except json.JSONDecodeError:
        # This is where we fall back to default values
        print("✗ JSON parsing failed - Falling back to defaults")
        default_score = 0.0  # Not 50.0!
        default_value = bad_response  # Keep the raw response for debugging
        print(f"  Default Score: {default_score}")
        print(f"  Raw response: {default_value[:50]}...")

def explain_why_zero_not_fifty():
    """Explain why 0.0 is better than 50.0 as default"""
    print("\nWhy use 0.0 instead of 50.0 when JSON parsing fails:")
    print("=" * 55)
    print("1. SEMANTIC MEANING:")
    print("   0.0 = 'No valid analysis' or 'Analysis failed'")
    print("   50.0 = 'Neutral analysis' (implies valid analysis)")
    print()
    print("2. SYSTEM BEHAVIOR:")
    print("   Stocks with 0.0 scores are typically filtered out")
    print("   Stocks with 50.0 scores might be considered for trading")
    print()
    print("3. ERROR HANDLING:")
    print("   0.0 makes it clear that there was a problem")
    print("   50.0 might hide the fact that LLM response was malformed")
    print()
    print("4. DEBUGGING:")
    print("   0.0 scores are easy to identify as problematic")
    print("   50.0 scores might be mistaken for valid neutral analysis")

if __name__ == "__main__":
    print("LLM Error Handling Test")
    print("=" * 25)
    print()

    test_json_parsing_success()
    print()
    test_json_parsing_failure()
    print()
    explain_why_zero_not_fifty()

