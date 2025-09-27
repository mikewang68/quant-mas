#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug specific test cases that are failing
"""

import re

def debug_failing_cases():
    """Debug the specific cases that are failing"""

    # Case 1: Content with "评分是0.65" format
    content1 = "综合考虑以上因素，我给出的基本面评分是0.65。这个评分反映了公司在盈利能力方面表现良好，但在营收增长方面存在不足。"

    print("Debugging Case 1:")
    print(f"Content: {content1}")

    # Test different patterns
    patterns = [
        r'(?:评分|score)[:：]?\s*(\d+\.?\d*)',
        r'评分[:：]?\s*(\d+\.?\d*)',
        r'评分为?(\d+\.?\d*)',
        r'(\d+\.?\d*)',
        r'评分是(\d+\.?\d*)'
    ]

    for i, pattern in enumerate(patterns, 1):
        matches = re.findall(pattern, content1, re.IGNORECASE)
        print(f"  Pattern {i} '{pattern}': {matches}")

    print()

    # Case 4: Content with "评分为0.75" format
    content4 = "综合评分0.75分。详细分析显示公司在行业中处于领先地位，评分为0.75。"

    print("Debugging Case 4:")
    print(f"Content: {content4}")

    for i, pattern in enumerate(patterns, 1):
        matches = re.findall(pattern, content4, re.IGNORECASE)
        print(f"  Pattern {i} '{pattern}': {matches}")

        # Test with specific match for this case
        if pattern == r'评分为?(\d+\.?\d*)':
            specific_matches = re.findall(r'评分为(\d+\.?\d*)', content4, re.IGNORECASE)
            print(f"    Specific '评分为': {specific_matches}")

    print()

if __name__ == "__main__":
    debug_failing_cases()

