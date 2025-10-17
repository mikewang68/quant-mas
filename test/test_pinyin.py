#!/usr/bin/env python3
"""
Test script to debug pinyin conversion and search functionality
"""

import sys
import os

# Add the project root to the Python path to resolve imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pypinyin

def get_pinyin_abbreviation(chinese_text: str) -> str:
    """
    Convert Chinese text to pinyin abbreviation.

    Args:
        chinese_text: Chinese text to convert

    Returns:
        Pinyin abbreviation (e.g., "平安银行" -> "PAYH")
    """
    if not chinese_text or not isinstance(chinese_text, str):
        return ""

    try:
        # Get pinyin for each character, take first letter of each pinyin
        pinyin_list = pypinyin.lazy_pinyin(chinese_text, style=pypinyin.Style.FIRST_LETTER)
        # Convert to uppercase and join
        abbreviation = ''.join(pinyin_list).upper()
        return abbreviation
    except Exception as e:
        print(f"Error converting {chinese_text} to pinyin: {e}")
        return ""

# Test the pinyin conversion for 润和软件
print("Testing pinyin conversion for 润和软件:")
result = get_pinyin_abbreviation("润和软件")
print(f"润和软件 -> {result}")

# Test search matching
search_terms = ["rhrj", "rh", "rj", "润和", "软件", "润和软件"]
for term in search_terms:
    term_lower = term.lower()
    matches_code = "300339".lower().startswith(term_lower)
    matches_name = term_lower in "润和软件".lower()
    matches_pinyin = term_lower in result.lower()

    print(f"\nSearch term: '{term}'")
    print(f"  Matches code (300339): {matches_code}")
    print(f"  Matches name (润和软件): {matches_name}")
    print(f"  Matches pinyin ({result}): {matches_pinyin}")
    print(f"  Would be found: {matches_code or matches_name or matches_pinyin}")

# Test with some other stocks for comparison
test_stocks = [
    "平安银行",
    "万科A",
    "浦发银行",
    "润和软件"
]

print("\n\nTesting pinyin conversion for various stocks:")
for stock in test_stocks:
    pinyin = get_pinyin_abbreviation(stock)
    print(f"{stock} -> {pinyin}")

