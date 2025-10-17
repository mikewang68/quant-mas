#!/usr/bin/env python3
"""
Find specific stocks in the database
"""

import sys
import os

# Add the project root to the Python path to resolve imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mongodb_manager import MongoDBManager

def find_specific_stocks():
    """Find specific stocks in the database"""
    try:
        # Initialize MongoDB manager
        mongo_manager = MongoDBManager()
        db = mongo_manager.db

        print("=== Finding Specific Stocks ===")

        # Check total count
        total_stocks = db.code.count_documents({})
        print(f"Total stocks in database: {total_stocks}")

        # Find specific stocks
        target_stocks = ["润和软件", "中科曙光", "平安银行"]

        for stock_name in target_stocks:
            print(f"\nLooking for: {stock_name}")
            stock = db.code.find_one({"name": stock_name})
            if stock:
                print(f"  Found: {stock.get('code')} - {stock.get('name')}")

                # Check if it's in the first 1000 stocks
                all_stocks = list(db.code.find().limit(1000))
                found_in_first_1000 = any(s.get('name') == stock_name for s in all_stocks)
                print(f"  In first 1000 stocks: {found_in_first_1000}")
            else:
                print("  NOT FOUND!")

        # Check if we need to load more stocks
        print(f"\n=== Loading all stocks ===")
        all_stocks_cursor = db.code.find()
        all_stocks = list(all_stocks_cursor)
        print(f"Loaded {len(all_stocks)} stocks")

        # Find our target stocks in the full list
        for stock_name in target_stocks:
            found = [s for s in all_stocks if s.get('name') == stock_name]
            if found:
                print(f"  {stock_name}: Found {len(found)} matches")
                for f in found:
                    print(f"    - {f.get('code')} - {f.get('name')}")
            else:
                print(f"  {stock_name}: NOT FOUND in full list!")

    except Exception as e:
        print(f"Error in find_specific_stocks: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    find_specific_stocks()

