#!/usr/bin/env python3
"""
Test script to verify the new search logic
"""

import sys
import os

# Add the project root to the Python path to resolve imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mongodb_manager import MongoDBManager
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

def test_new_search_logic():
    """Test the new search logic"""
    try:
        # Initialize MongoDB manager
        mongo_manager = MongoDBManager()
        db = mongo_manager.db

        print("=== Testing New Search Logic ===")

        # Get all stocks
        stocks_cursor = db.code.find().limit(1000)
        all_stocks = []
        for stock in stocks_cursor:
            all_stocks.append({
                "code": stock.get("code", ""),
                "name": stock.get("name", ""),
                "pinyin": stock.get("pinyin", "")
            })

        # Test cases
        test_cases = [
            ("300339", "numeric - should find 润和软件"),
            ("603019", "numeric - should find 中科曙光"),
            ("润和软件", "chinese - should find 润和软件"),
            ("中科曙光", "chinese - should find 中科曙光"),
            ("rhrj", "english - should find 润和软件"),
            ("平安", "chinese - should find 平安银行"),
            ("payh", "english - should find 平安银行")
        ]

        for search_term, description in test_cases:
            print(f"\nTesting: '{search_term}' ({description})")

            search_term_lower = search_term.lower()
            matched_stocks = []

            # Determine search type based on input
            is_numeric = search_term.isdigit()
            is_chinese = any('一' <= char <= '鿿' for char in search_term)
            is_english = search_term.isalpha()

            print(f"  Type: numeric={is_numeric}, chinese={is_chinese}, english={is_english}")

            for stock in all_stocks:
                # If input is numbers, search by stock code
                if is_numeric:
                    if stock["code"].startswith(search_term):
                        matched_stocks.append(stock)
                        continue

                # If input is Chinese characters, search by stock name
                elif is_chinese:
                    if stock["name"] and search_term in stock["name"]:
                        matched_stocks.append(stock)
                        continue

                # If input is English letters, search by pinyin abbreviation
                elif is_english:
                    # Generate pinyin abbreviation if not already in database
                    pinyin_abbr = stock.get("pinyin", "")
                    if not pinyin_abbr and stock["name"]:
                        pinyin_abbr = get_pinyin_abbreviation(stock["name"])

                    if pinyin_abbr and search_term_lower in pinyin_abbr.lower():
                        matched_stocks.append(stock)
                        continue

            print(f"  Found {len(matched_stocks)} matches")
            for match in matched_stocks:
                print(f"    - {match['code']} - {match['name']}")

    except Exception as e:
        print(f"Error in test_new_search_logic: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_new_search_logic()

