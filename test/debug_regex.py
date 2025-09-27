#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug script to test regex patterns for score extraction
"""

import re

def test_regex_patterns():
    """Test different regex patterns for score extraction"""

    test_contents = [
        "综合考虑以上因素，我给出的基本面评分是0.65。这个评分反映了公司在盈利能力方面表现良好，但在营收增长方面存在不足。",
        "基于以上分析，该股票的基本面得分为85分。这表明公司具有较强的市场竞争力。",
        "综合评分0.75分。详细分析显示公司在行业中处于领先地位，评分为0.75。",
        "该公司财务状况良好，业务发展稳定。建议关注后续财报数据。"
    ]

    # Test different regex patterns
    patterns = [
        r'(?:评分|score)[:：]?\s*(\d+\.?\d*)',
        r'评分[:：]?\s*(\d+\.?\d*)',
        r'(\d+\.?\d*)分',
        r'得分[:：]?\s*(\d+\.?\d*)',
        r'评分为?(\d+\.?\d*)',
    ]

    for i, content in enumerate(test_contents, 1):
        print(f"Test content {i}: {content}")

        for j, pattern in enumerate(patterns, 1):
            matches = re.findall(pattern, content, re.IGNORECASE)
            print(f"  Pattern {j} '{pattern}': {matches}")

        print()

if __name__ == "__main__":
    test_regex_patterns()

