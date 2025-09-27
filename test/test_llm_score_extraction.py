#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to validate LLM score extraction logic
"""

import sys
import os
import json
import re

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_score_extraction():
    """Test score extraction from various content formats"""

    # Test cases with different content formats
    test_cases = [
        # Case 1: Content with score in text
        {
            "content": "综合考虑以上因素，我给出的基本面评分是0.65。这个评分反映了公司在盈利能力方面表现良好，但在营收增长方面存在不足。",
            "expected_score": 0.65
        },
        # Case 2: Content with score in different format
        {
            "content": "基于以上分析，该股票的基本面得分为85分。这表明公司具有较强的市场竞争力。",
            "expected_score": 0.85  # Should be normalized from 85 to 0.85
        },
        # Case 3: Content without explicit score
        {
            "content": "该公司财务状况良好，业务发展稳定。建议关注后续财报数据。",
            "expected_score": 0.0  # Default when no score found
        },
        # Case 4: Content with multiple score mentions (should pick the first)
        {
            "content": "综合评分0.75分。详细分析显示公司在行业中处于领先地位，评分为0.75。",
            "expected_score": 0.75
        }
    ]

    print("Testing score extraction logic...")

    for i, test_case in enumerate(test_cases, 1):
        content = test_case["content"]
        expected_score = test_case["expected_score"]

        # Extract score using regex (same logic as in the strategy)
        llm_score = 0.0  # Default score

        # Try multiple patterns to catch different formats
        patterns = [
            r'(?:评分|score)[:：]?\s*(\d+\.?\d*)',  # General pattern
            r'评分是(\d+\.?\d*)',                   # "评分是0.65" format
            r'评分为?(\d+\.?\d*)',                  # "评分为0.75" or "评分0.75" format
            r'得分为?(\d+\.?\d*)',                  # "得分为85" format
            r'(\d+\.?\d*)分'                        # "85分" format
        ]

        score_matches = []
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                score_matches = matches
                break

        if score_matches:
            try:
                extracted_score = float(score_matches[0])
                # If score is in 0-100 range, normalize to 0-1 range
                if 0 <= extracted_score <= 100:
                    llm_score = max(0.0, min(1.0, extracted_score / 100.0))
                elif 0 <= extracted_score <= 1:
                    llm_score = extracted_score
            except ValueError:
                pass  # If we can't parse the extracted score, keep default

        print(f"Test case {i}:")
        print(f"  Content: {content}")
        print(f"  Expected score: {expected_score}")
        print(f"  Extracted score: {llm_score}")
        print(f"  Result: {'✓ PASS' if abs(llm_score - expected_score) < 0.01 else '✗ FAIL'}")
        print()

def test_fallback_logic():
    """Test the fallback logic when JSON parsing fails"""

    print("Testing fallback logic...")

    # Simulate raw content that would fail JSON parsing
    raw_content = '''{
    "score": 0.65,
    "value": "综合考虑以上因素，我给出的基本面评分是0.65。这个评分反映了公司在盈利能力方面表现良好，但在营收增长方面存在不足。\\x00\\x01"
}'''

    # Test the fallback logic
    llm_score = 0.0  # Default score (not 50.0!)
    llm_value = raw_content

    # Try to extract score from raw content using regex
    score_matches = re.findall(r'(?:评分|score)[:：]?\s*(\d+\.?\d*)', raw_content, re.IGNORECASE)
    if score_matches:
        try:
            extracted_score = float(score_matches[0])
            # If score is in 0-100 range, normalize to 0-1 range
            if 0 <= extracted_score <= 100:
                llm_score = max(0.0, min(1.0, extracted_score / 100.0))
            elif 0 <= extracted_score <= 1:
                llm_score = extracted_score
        except ValueError:
            pass  # If we can't parse the extracted score, keep default

    print(f"Raw content: {raw_content}")
    print(f"Extracted score: {llm_score}")
    print(f"Value (raw content): {llm_value}")
    print()

    # Test with content that has no score
    no_score_content = "该公司财务状况良好，业务发展稳定。建议关注后续财报数据。"

    llm_score = 0.0  # Default score
    llm_value = no_score_content

    score_matches = re.findall(r'(?:评分|score)[:：]?\s*(\d+\.?\d*)', no_score_content, re.IGNORECASE)
    if score_matches:
        try:
            extracted_score = float(score_matches[0])
            # If score is in 0-100 range, normalize to 0-1 range
            if 0 <= extracted_score <= 100:
                llm_score = max(0.0, min(1.0, extracted_score / 100.0))
            elif 0 <= extracted_score <= 1:
                llm_score = extracted_score
        except ValueError:
            pass

    print(f"Content without score: {no_score_content}")
    print(f"Extracted score: {llm_score} (should be 0.0)")
    print(f"Value: {llm_value}")
    print()

def explain_why_zero_not_fifty():
    """Explain why using 0.0 instead of 50.0 as default is better"""

    print("Why use 0.0 instead of 50.0 as default score?")
    print("=" * 50)
    print("1. Semantic meaning:")
    print("   - 0.0 means 'no information' or 'analysis failed'")
    print("   - 50.0 means 'neutral' which implies some analysis was done")
    print()
    print("2. System behavior:")
    print("   - Stocks with 0.0 scores are typically filtered out or given low priority")
    print("   - Stocks with 50.0 scores might be considered for further analysis")
    print()
    print("3. Error handling:")
    print("   - When JSON parsing fails, it's better to be conservative")
    print("   - A 0.0 score clearly indicates a problem that needs attention")
    print()
    print("4. Debugging:")
    print("   - 0.0 scores are easier to identify as problematic in logs")
    print("   - 50.0 scores might be mistaken for valid neutral analysis")
    print()

if __name__ == "__main__":
    print("LLM Score Extraction Test Suite")
    print("=" * 40)
    print()

    test_score_extraction()
    test_fallback_logic()
    explain_why_zero_not_fifty()

    print("Test completed!")

