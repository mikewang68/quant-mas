#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Detailed debug of regex patterns
"""

import re

def debug_regex_detailed():
    """Debug regex patterns in detail"""

    # Test case 1: "评分是0.65"
    content1 = "综合考虑以上因素，我给出的基本面评分是0.65。这个评分反映了公司在盈利能力方面表现良好，但在营收增长方面存在不足。"

    print("Content 1:", content1)
    print()

    # Test each pattern individually
    patterns = [
        (r'(?:评分|score)[:：]?\\s*(\\d+\\.?\\d*)', "General pattern"),
        (r'评分是(\\d+\\.?\\d*)', '"评分是" pattern'),
        (r'评分为?(\\d+\\.?\\d*)', '"评分为" pattern'),
        (r'得分为?(\\d+\\.?\\d*)', '"得分为" pattern'),
        (r'(\\d+\\.?\\d*)分', '"XX分" pattern')
    ]

    for pattern, description in patterns:
        # Remove extra escaping for direct testing
        clean_pattern = pattern.replace('\\\\', '\\')
        matches = re.findall(clean_pattern, content1, re.IGNORECASE)
        print(f"{description}: '{clean_pattern}' -> {matches}")

    print()

    # Test case 4: Multiple scores
    content4 = "综合评分0.75分。详细分析显示公司在行业中处于领先地位，评分为0.75。"

    print("Content 4:", content4)
    print()

    for pattern, description in patterns:
        # Remove extra escaping for direct testing
        clean_pattern = pattern.replace('\\\\', '\\')
        matches = re.findall(clean_pattern, content4, re.IGNORECASE)
        print(f"{description}: '{clean_pattern}' -> {matches}")

if __name__ == "__main__":
    debug_regex_detailed()

