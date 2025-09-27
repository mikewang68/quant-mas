#!/usr/bin/env python3
"""
Debug script to examine the exact database record for stock 000061
"""

import sys
import os
import json

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mongodb_manager import MongoDBManager

def debug_database_record():
    """Examine the exact database record for stock 000061"""

    # Initialize database manager
    db_manager = MongoDBManager()

    # Get pool collection
    pool_collection = db_manager.db["pool"]

    # Find the latest pool record
    latest_pool_record = pool_collection.find_one(sort=[("selection_date", -1)])

    if not latest_pool_record:
        print("No records found in pool collection")
        return

    print(f"Latest pool record date: {latest_pool_record.get('selection_date', 'Unknown')}")

    # Extract stocks from the latest record
    stocks = latest_pool_record.get("stocks", [])

    # Find the specific stock
    target_stock = None
    for stock in stocks:
        if stock.get("code") == "000061":
            target_stock = stock
            break

    if not target_stock:
        print("Stock 000061 not found in latest pool record")
        return

    print(f"Found stock 000061")
    print(f"Basic stock info: code={target_stock.get('code')}, score={target_stock.get('score')}")

    # Check if fund data exists
    if "fund" not in target_stock:
        print("No fund data found for this stock")
        return

    fund_data = target_stock["fund"]
    print(f"Fund data found with {len(fund_data)} strategies")

    # Display fund data for each strategy
    for strategy_name, strategy_data in fund_data.items():
        print(f"\nStrategy: {strategy_name}")
        print(f"  Score: {strategy_data.get('score', 'N/A')}")
        value_field = strategy_data.get('value', 'N/A')
        print(f"  Value type: {type(value_field)}")
        if isinstance(value_field, str):
            print(f"  Value length: {len(value_field)}")
            print(f"  Value (first 300 chars): {value_field[:300]}")

            # Check if value contains score information
            score_in_value = str(strategy_data.get('score', '')) in value_field
            if score_in_value:
                print("  *** ISSUE DETECTED: Score found in value field ***")

            # Try to parse value as JSON to see if it's nested
            try:
                parsed_value = json.loads(value_field)
                if isinstance(parsed_value, dict):
                    print(f"  *** NESTED JSON DETECTED ***")
                    print(f"    Nested keys: {list(parsed_value.keys())}")
                    if 'score' in parsed_value:
                        print(f"    Nested score: {parsed_value['score']}")
                    if 'value' in parsed_value:
                        print(f"    Nested value length: {len(str(parsed_value['value']))}")
                        print(f"    Nested value (first 100 chars): {str(parsed_value['value'])[:100]}")
            except json.JSONDecodeError:
                pass  # Not a JSON string
        else:
            print(f"  Value: {value_field}")

if __name__ == "__main__":
    debug_database_record()

