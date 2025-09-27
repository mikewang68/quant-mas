#!/usr/bin/env python3
"""
Verify that the LLM nested JSON parsing fix resolves the score=0 issues in the database.
This script checks actual database records to verify the fix.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mongodb_manager import MongoDBManager
import json

def check_database_records():
    """Check database records for the score=0 but value has data issue."""
    print("Checking database records for score=0 issues...")

    try:
        # Connect to database
        db_manager = MongoDBManager()
        pool_collection = db_manager.db['pool']

        # Get the latest pool record
        latest_record = pool_collection.find_one(sort=[('selection_date', -1)])

        if not latest_record:
            print("No pool records found")
            return

        print(f"Latest pool record date: {latest_record.get('selection_date', 'Unknown')}")

        # Check stocks with fund data
        stocks = latest_record.get('stocks', [])
        print(f"Total stocks: {len(stocks)}")

        # Count issues
        total_issues = 0
        fixed_issues = 0
        unresolved_issues = 0

        for stock in stocks:
            if 'fund' in stock:
                code = stock.get('code', 'Unknown')
                fund_data = stock['fund']

                for strategy_name, strategy_data in fund_data.items():
                    score = strategy_data.get('score', 'N/A')
                    value = strategy_data.get('value', 'N/A')

                    # Check for the issue: value has data but score is 0
                    if score == 0 or score == 0.0:
                        if value != 'N/A' and value and len(str(value)) > 10:
                            total_issues += 1
                            print(f"  Issue found - Stock {code}, Strategy '{strategy_name}': score={score}")

                            # Try to parse the value as JSON to see if it contains nested score
                            if isinstance(value, str):
                                try:
                                    nested_data = json.loads(value)
                                    if isinstance(nested_data, dict) and 'score' in nested_data:
                                        nested_score = float(nested_data['score'])
                                        print(f"    Nested score found: {nested_score}")
                                        if nested_score > 0:
                                            print(f"    *** This issue WOULD BE FIXED by the patch ***")
                                            fixed_issues += 1
                                        else:
                                            print(f"    Nested score is also 0, issue remains")
                                            unresolved_issues += 1
                                    else:
                                        print(f"    Value is string but not valid JSON with score")
                                        unresolved_issues += 1
                                except json.JSONDecodeError:
                                    print(f"    Value is string but not valid JSON")
                                    unresolved_issues += 1
                            else:
                                print(f"    Value is not a string")
                                unresolved_issues += 1

        print(f"\nSummary:")
        print(f"  Total issues found: {total_issues}")
        print(f"  Issues that would be fixed by patch: {fixed_issues}")
        print(f"  Remaining unresolved issues: {unresolved_issues}")

        db_manager.close_connection()

    except Exception as e:
        print(f"Error checking database records: {e}")

def main():
    """Main verification function."""
    print("Verifying LLM nested JSON parsing fix...")
    print("=" * 60)

    check_database_records()

    print("=" * 60)
    print("Verification completed!")

if __name__ == "__main__":
    main()

