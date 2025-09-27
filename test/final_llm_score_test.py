#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Final test script to demonstrate LLM score extraction logic
"""

import re

def extract_score_from_content(content):
    """
    Extract score from content using improved regex patterns.
    This is the logic used in the LLM fundamental strategy.
    """
    llm_score = 0.0  # Default score

    # Try multiple patterns to catch different formats
    patterns = [
        r'评分是(\d+\.?\d*)',      # "评分是0.65" format
        r'(?:评分|score)[:：]?\s*(\d+\.?\d*)',  # General pattern
        r'评分为?(\d+\.?\d*)',     # "评分为0.75" or "评分0.75" format
        r'得分为?(\d+\.?\d*)',     # "得分为85" format
        r'(\d+\.?\d*)分'           # "85分" format
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

    return llm_score

def test_score_extraction():
    """Test score extraction with various content formats"""

    test_cases = [
        {
            "name": "评分是0.65格式",
            "content": "综合考虑以上因素，我给出的基本面评分是0.65。这个评分反映了公司在盈利能力方面表现良好，但在营收增长方面存在不足。",
            "expected": 0.65
        },
        {
            "name": "得分为85分格式",
            "content": "基于以上分析，该股票的基本面得分为85分。这表明公司具有较强的市场竞争力。",
            "expected": 0.85
        },
        {
            "name": "无分数内容",
            "content": "该公司财务状况良好，业务发展稳定。建议关注后续财报数据。",
            "expected": 0.0
        },
        {
            "name": "评分为0.75格式",
            "content": "综合评分0.75分。详细分析显示公司在行业中处于领先地位，评分为0.75。",
            "expected": 0.75
        }
    ]

    print("LLM Score Extraction Test Results")
    print("=" * 40)

    all_passed = True
    for test_case in test_cases:
        extracted = extract_score_from_content(test_case["content"])
        passed = abs(extracted - test_case["expected"]) < 0.01
        if not passed:
            all_passed = False

        print(f"{test_case['name']}:")
        print(f"  Content: {test_case['content'][:30]}...")
        print(f"  Expected: {test_case['expected']}")
        print(f"  Extracted: {extracted}")
        print(f"  Result: {'✓ PASS' if passed else '✗ FAIL'}")
        print()

    return all_passed

def explain_why_zero_not_fifty():
    """Explain why using 0.0 instead of 50.0 as default score"""

    print("Why use 0.0 instead of 50.0 as default score?")
    print("=" * 50)
    print()
    print("1. SEMANTIC MEANING:")
    print("   - 0.0 means 'no information' or 'analysis failed'")
    print("   - 50.0 means 'neutral' which implies some analysis was done")
    print()
    print("2. SYSTEM BEHAVIOR:")
    print("   - Stocks with 0.0 scores are typically filtered out")
    print("   - Stocks with 50.0 scores might be considered for analysis")
    print()
    print("3. ERROR HANDLING:")
    print("   - When JSON parsing fails, it's better to be conservative")
    print("   - A 0.0 score clearly indicates a problem")
    print()
    print("4. DEBUGGING:")
    print("   - 0.0 scores are easier to identify as problematic in logs")
    print("   - 50.0 scores might be mistaken for valid neutral analysis")
    print()

if __name__ == "__main__":
    print("Final LLM Score Extraction Test")
    print("=" * 40)
    print()

    # Run tests
    tests_passed = test_score_extraction()

    # Explain reasoning
    explain_why_zero_not_fifty()

    # Summary
    print("SUMMARY:")
    print("=" * 10)
    if tests_passed:
        print("✓ All tests passed! The score extraction logic works correctly.")
    else:
        print("✗ Some tests failed. The logic needs further refinement.")

    print()
    print("CONCLUSION:")
    print("The LLM fundamental strategy now properly handles JSON parsing failures")
    print("by attempting to extract scores from raw content, using 0.0 as a safe")
    print("default value when no score can be extracted.")

