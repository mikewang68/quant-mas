#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug pattern matching for specific cases
"""

import re

def debug_pattern_matching():
    """Debug pattern matching for failing cases"""

    # Case 1: "评分是0.65"
    content1 = "综合考虑以上因素，我给出的基本面评分是0.65。这个评分反映了公司在盈利能力方面表现良好，但在营收增长方面存在不足。"

    print("Debugging Case 1:")
    print(f"Content: {content1}")
    print()

    # Test patterns one by one
    patterns = [
        r'(?:评分|score)[:：]?\s*(\d+\.?\d*)',  # General pattern
        r'评分是(\d+\.?\d*)',                   # "评分是0.65" format
        r'评分为?(\d+\.?\d*)',                  # "评分为0.75" or "评分0.75" format
        r'得分为?(\d+\.?\d*)',                  # "得分为85" format
        r'(\d+\.?\d*)分'                        # "85分" format
    ]

    for i, pattern in enumerate(patterns, 1):
        matches = re.findall(pattern, content1, re.IGNORECASE)
        print(f"Pattern {i}: '{pattern}' -> Matches: {matches}")
        if matches:
            try:
                score = float(matches[0])
                print(f"  Extracted score: {score}")
            except ValueError as e:
                print(f"  Error converting to float: {e}")
        print()

    # Case 4: Multiple scores
    content4 = "综合评分0.75分。详细分析显示公司在行业中处于领先地位，评分为0.75。"

    print("Debugging Case 4:")
    print(f"Content: {content4}")
    print()

    for i, pattern in enumerate(patterns, 1):
        matches = re.findall(pattern, content4, re.IGNORECASE)
        print(f"Pattern {i}: '{pattern}' -> Matches: {matches}")
        if matches:
            try:
                score = float(matches[0])
                print(f"  Extracted score: {score}")
            except ValueError as e:
                print(f"  Error converting to float: {e}")
        print()

if __name__ == "__main__":
    debug_pattern_matching()

