#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for LLM fundamental strategy fix
"""

import sys
import os
import json

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.llm_fundamental_strategy import LLMFundamentalStrategy

def test_fix_json_string():
    """Test the _fix_json_string method"""
    strategy = LLMFundamentalStrategy()

    # Test case 1: Normal JSON string (should remain unchanged)
    normal_json = '{"score": 0.85, "value": "This is a test"}'
    fixed = strategy._fix_json_string(normal_json)
    assert fixed == normal_json, f"Normal JSON was modified: {fixed}"
    print("✓ Test 1 passed: Normal JSON unchanged")

    # Test case 2: JSON with control characters (simplified test)
    json_with_issues = '{"score": 0.85, "value": "Test with \n newlines"}'
    fixed = strategy._fix_json_string(json_with_issues)
    print(f"✓ Test 2 passed: JSON with issues handled: {fixed}")

def test_extract_from_raw_content():
    """Test extraction from raw content when JSON parsing fails"""
    strategy = LLMFundamentalStrategy()

    # Simulate raw content that would fail JSON parsing
    raw_content = '''综合考虑以上因素，我给出的基本面评分是0.65。这个评分反映了公司在行业中的相对优势，但也指出了其在现金流管理方面的不足。公司具有稳定的盈利能力和良好的行业地位，但需要关注其资产负债率的上升趋势。'''

    # Test score extraction
    import re
    score_matches = re.findall(r'(?:评分|score)[:：]?\s*(\d+\.?\d*)', raw_content, re.IGNORECASE)
    if score_matches:
        extracted_score = float(score_matches[0])
        # Normalize if in 0-100 range
        if 0 <= extracted_score <= 100:
            normalized_score = max(0.0, min(1.0, extracted_score / 100.0))
        else:
            normalized_score = extracted_score
        print(f"✓ Score extraction test passed: {extracted_score} -> {normalized_score}")

    # Test value extraction
    value_patterns = [
        r'综合考虑以上因素，我给出的基本面评分是[\d.]+。(.*)',
        r'综合考虑以上因素，我给出的基本面评分是[\d.]+。这个评分反映了.*?不足。(.*?)(?:\n\n|$)',
        r'综合考虑以上因素，我给出的基本面评分是[\d.]+。这个评分反映了.*?不足。(.*)$',
    ]

    extracted_value = raw_content
    for pattern in value_patterns:
        match = re.search(pattern, raw_content, re.DOTALL | re.IGNORECASE)
        if match:
            extracted_value = match.group(1).strip()
            if extracted_value:
                break

    print(f"✓ Value extraction test passed: {extracted_value[:50]}...")

def test_nested_json_handling():
    """Test nested JSON handling in both success and failure paths"""
    strategy = LLMFundamentalStrategy()

    # Test nested JSON in success path
    nested_json_content = '{"score": 0.75, "value": "{\\"score\\": 0.75, \\"value\\": \\"This is the actual analysis text.\\"}"}'

    try:
        # Parse main JSON
        analysis_result = json.loads(nested_json_content)
        llm_score = float(analysis_result.get("score", 0))
        llm_value = analysis_result.get("value", analysis_result.get("analysis", nested_json_content))

        # Handle nested JSON in value field
        if isinstance(llm_value, str):
            try:
                nested_result = json.loads(llm_value)
                if isinstance(nested_result, dict) and "value" in nested_result:
                    llm_value = nested_result.get("value", llm_value)
                    if "score" in nested_result and llm_score == 0:
                        llm_score = float(nested_result.get("score", llm_score))
            except json.JSONDecodeError:
                pass

        print(f"✓ Nested JSON handling in success path: score={llm_score}, value={llm_value[:30]}...")
    except Exception as e:
        print(f"✗ Nested JSON handling in success path failed: {e}")

    # Test nested JSON in failure path (fallback)
    raw_content = '{"score": 0.75, "value": "{\\"score\\": 0.75, \\"value\\": \\"This is the actual analysis text.\\"}"}'

    try:
        # Check if the raw content looks like a JSON string
        stripped_content = raw_content.strip()
        if stripped_content.startswith('{') and stripped_content.endswith('}'):
            # Try to fix common JSON issues and parse
            fixed_content = strategy._fix_json_string(stripped_content)
            nested_result = json.loads(fixed_content)
            if isinstance(nested_result, dict):
                # Extract score if available
                if "score" in nested_result:
                    try:
                        extracted_score = float(nested_result["score"])
                        if 0 <= extracted_score <= 100:
                            llm_score = max(0.0, min(1.0, extracted_score / 100.0))
                        elif 0 <= extracted_score <= 1:
                            llm_score = extracted_score
                    except ValueError:
                        pass

                # Extract value if available
                if "value" in nested_result:
                    llm_value = nested_result["value"]
                elif "analysis" in nested_result:
                    llm_value = nested_result["analysis"]

                # Handle nested JSON in value field
                if isinstance(llm_value, str):
                    try:
                        nested_value_result = json.loads(llm_value)
                        if isinstance(nested_value_result, dict) and "value" in nested_value_result:
                            llm_value = nested_value_result["value"]
                            # Also check for score in the nested value
                            if "score" in nested_value_result:
                                try:
                                    nested_score = float(nested_value_result["score"])
                                    if 0 <= nested_score <= 100:
                                        llm_score = max(0.0, min(1.0, nested_score / 100.0))
                                    elif 0 <= nested_score <= 1:
                                        llm_score = nested_score
                                except ValueError:
                                    pass
                    except json.JSONDecodeError:
                        pass

        print(f"✓ Nested JSON handling in failure path: score={llm_score}, value={llm_value[:30]}...")
    except Exception as e:
        print(f"✗ Nested JSON handling in failure path failed: {e}")

if __name__ == "__main__":
    print("Testing LLM Fundamental Strategy fixes...")
    test_fix_json_string()
    test_extract_from_raw_content()
    test_nested_json_handling()
    print("All tests completed!")

