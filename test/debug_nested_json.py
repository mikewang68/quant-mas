#!/usr/bin/env python3
"""
Debug script to test nested JSON handling
"""

import json

# Simulate the LLM response - simplified version
llm_response = '''{
    "score": 0.65,
    "value": "{\\"score\\": 0.65, \\"value\\": \\"This is the actual analysis text.\\"}"
}'''

print("LLM Response:")
print(llm_response)

# Parse the main JSON
analysis_result = json.loads(llm_response)
print("\nMain analysis result:")
print(f"Score: {analysis_result.get('score')}")
print(f"Value: {analysis_result.get('value')}")
print(f"Value type: {type(analysis_result.get('value'))}")

# Try to parse the nested JSON
llm_score = float(analysis_result.get("score", 0))
llm_value = analysis_result.get("value", analysis_result.get("analysis", llm_response))

print("\nBefore nested JSON handling:")
print(f"llm_score: {llm_score}")
print(f"llm_value type: {type(llm_value)}")

# Handle case where the value field itself contains a nested JSON object
# This can happen when the LLM returns a JSON string in the value field
if isinstance(llm_value, str):
    try:
        # Try to parse the value field as JSON
        nested_result = json.loads(llm_value)
        print(f"\nNested result: {nested_result}")
        print(f"Nested result type: {type(nested_result)}")
        if isinstance(nested_result, dict) and "value" in nested_result:
            # If it's a nested structure with score and value, extract the actual value
            llm_value = nested_result.get("value", llm_value)
            print(f"Extracted llm_value: {llm_value}")
            # If there's also a score in the nested structure, use it if not already set
            if "score" in nested_result and llm_score == 0:
                llm_score = float(nested_result.get("score", llm_score))
                print(f"Updated llm_score from nested: {llm_score}")
    except json.JSONDecodeError as e:
        # If parsing fails, keep the original value
        print(f"Failed to parse nested JSON: {e}")
        pass

print("\nAfter nested JSON handling:")
print(f"llm_score: {llm_score}")
print(f"llm_value type: {type(llm_value)}")
if isinstance(llm_value, str):
    print(f"llm_value (first 100 chars): {llm_value[:100]}")

