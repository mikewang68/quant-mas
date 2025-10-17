#!/usr/bin/env python3
"""
Debug script to test web application search functionality
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

def debug_web_search():
    """Debug web application search functionality"""
    try:
        # Initialize MongoDB manager (same as web app)
        mongo_manager = MongoDBManager()
        db = mongo_manager.db

        print("=== Testing Web Application Search ===")

        # Test 1: Check if 润和软件 exists in code collection
        print("\n1. Checking if 润和软件 exists in code collection:")
        stock = db.code.find_one({"name": "润和软件"})
        if stock:
            print(f"   Found: {stock}")
        else:
            print("   NOT FOUND!")

        # Test 2: Check if 中科曙光 exists
        print("\n2. Checking if 中科曙光 exists in code collection:")
        stock2 = db.code.find_one({"name": "中科曙光"})
        if stock2:
            print(f"   Found: {stock2}")
        else:
            print("   NOT FOUND!")

        # Test 3: Count total stocks in code collection
        print("\n3. Counting total stocks in code collection:")
        total_stocks = db.code.count_documents({})
        print(f"   Total stocks: {total_stocks}")

        # Test 4: Get sample stocks
        print("\n4. Getting sample stocks:")
        sample_stocks = list(db.code.find().limit(5))
        for s in sample_stocks:
            print(f"   {s.get('code')} - {s.get('name')}")

        # Test 5: Simulate the web app search logic
        print("\n5. Simulating web app search logic:")
        search_terms = ["rhrj", "润和软件", "中科曙光", "300339", "603019"]

        for search_term in search_terms:
            print(f"\n   Testing search term: '{search_term}'")

            # Get all stocks (as web app does)
            stocks_cursor = db.code.find().limit(1000)
            all_stocks = []
            for stock in stocks_cursor:
                all_stocks.append({
                    "code": stock.get("code", ""),
                    "name": stock.get("name", ""),
                    "pinyin": stock.get("pinyin", "")
                })

            search_term_lower = search_term.lower()
            matched_stocks = []

            for stock in all_stocks:
                # Check if search term matches code (case-insensitive)
                if stock["code"].lower().startswith(search_term_lower):
                    matched_stocks.append(stock)
                    continue

                # Check if search term matches name (case-insensitive)
                if stock["name"] and search_term_lower in stock["name"].lower():
                    matched_stocks.append(stock)
                    continue

                # Check if search term matches pinyin abbreviation (case-insensitive)
                # Generate pinyin abbreviation if not already in database
                pinyin_abbr = stock.get("pinyin", "")
                if not pinyin_abbr and stock["name"]:
                    pinyin_abbr = get_pinyin_abbreviation(stock["name"])

                if pinyin_abbr and search_term_lower in pinyin_abbr.lower():
                    matched_stocks.append(stock)
                    continue

            print(f"   Found {len(matched_stocks)} matches")
            for match in matched_stocks:
                print(f"     - {match['code']} - {match['name']}")

    except Exception as e:
        print(f"Error in debug_web_search: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_web_search()

