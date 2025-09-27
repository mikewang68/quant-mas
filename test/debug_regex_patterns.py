#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug regex patterns for score extraction
"""

import re

def debug_patterns():
    """Debug regex patterns for different content formats"""

    test_cases = [
        "综合考虑以上因素，我给出的基本面评分是0.65。这个评分反映了公司在盈利能力方面表现良好，但在营收增长方面存在不足。",
        "综合评分0.75分。详细分析显示公司在行业中处于领先地位，评分为0.75。",
        "基于以上分析，该股票的基本面得分为85分。这表明公司具有较强的市场竞争力。"
    ]

    patterns = [
        r'(?:评分|score)[:：]?\s*(\d+\.?\d*)',  # General pattern
        r'评分是(\d+\.?\d*)',                   # "评分是0.65" format
        r'评分为?(\d+\.?\d*)',                  # "评分为0.75" or "评分0.75" format
        r'得分为?(\d+\.?\d*)',                  # "得分为85" format
        r'(\d+\.?\d*)分'                        # "85分" format
    ]

    for i, content in enumerate(test_cases, 1):
        print(f"Test case {i}: {content}")

        for j, pattern in enumerate(patterns, 1):
            matches = re.findall(pattern, content, re.IGNORECASE)
            print(f"  Pattern {j} '{pattern}': {matches}")

        print()

if __name__ == "__main__":
    debug_patterns()

