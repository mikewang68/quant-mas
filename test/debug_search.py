#!/usr/bin/env python3
"""
Debug script to test search functionality for 润和软件
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

def debug_search():
    """Debug search functionality"""
    try:
        # Initialize MongoDB manager
        mongo_manager = MongoDBManager()
        db = mongo_manager.db

        # Get all stocks from code collection
        stocks_cursor = db.code.find().limit(1000)
        all_stocks = []
        for stock in stocks_cursor:
            all_stocks.append({
                "code": stock.get("code", ""),
                "name": stock.get("name", ""),
                "pinyin": stock.get("pinyin", "")
            })

        print(f"Total stocks in database: {len(all_stocks)}")

        # Test search for 润和软件
        search_terms = ["rhrj", "润和软件", "润和", "软件", "300339"]

        for search_term in search_terms:
            print(f"\n=== Testing search term: '{search_term}' ===")
            search_term_lower = search_term.lower()
            matched_stocks = []

            for stock in all_stocks:
                # Check if search term matches code (case-insensitive)
                if stock["code"].lower().startswith(search_term_lower):
                    print(f"  Found by code: {stock['code']} - {stock['name']}")
                    matched_stocks.append(stock)
                    continue

                # Check if search term matches name (case-insensitive)
                if stock["name"] and search_term_lower in stock["name"].lower():
                    print(f"  Found by name: {stock['code']} - {stock['name']}")
                    matched_stocks.append(stock)
                    continue

                # Check if search term matches pinyin abbreviation (case-insensitive)
                # Generate pinyin abbreviation if not already in database
                pinyin_abbr = stock.get("pinyin", "")
                if not pinyin_abbr and stock["name"]:
                    pinyin_abbr = get_pinyin_abbreviation(stock["name"])

                if pinyin_abbr and search_term_lower in pinyin_abbr.lower():
                    print(f"  Found by pinyin: {stock['code']} - {stock['name']} (pinyin: {pinyin_abbr})")
                    matched_stocks.append(stock)
                    continue

            print(f"  Total matches: {len(matched_stocks)}")

        # Specifically check for 润和软件
        print("\n=== Checking specifically for 润和软件 ===")
        for stock in all_stocks:
            if stock["name"] == "润和软件":
                print(f"Found 润和软件: {stock}")
                pinyin_abbr = get_pinyin_abbreviation(stock["name"])
                print(f"Pinyin abbreviation: {pinyin_abbr}")
                print(f"Does 'rhrj' match pinyin? {'rhrj' in pinyin_abbr.lower()}")
                break
        else:
            print("润和软件 not found in database!")

    except Exception as e:
        print(f"Error in debug_search: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_search()

