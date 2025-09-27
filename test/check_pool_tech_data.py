#!/usr/bin/env python3
"""
Check pool tech data in database
"""

import sys
import os
from datetime import datetime

# Add the project root directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mongodb_manager import MongoDBManager

def check_pool_data():
    """Check pool data in database"""
    print("Checking pool data in database...")

    # Initialize components
    db_manager = MongoDBManager()

    try:
        # Check pool collection
        pool_collection = db_manager.db["pool"]
        latest_pool_record = pool_collection.find_one(sort=[("selection_date", -1)])

        if not latest_pool_record:
            print("ERROR: No records found in pool collection")
            return False

        print(f"Found latest pool record with ID: {latest_pool_record.get('_id')}")
        print(f"Selection date: {latest_pool_record.get('selection_date')}")
        print(f"Tech at: {latest_pool_record.get('tech_at')}")

        # Extract stock codes
        pool_stocks = latest_pool_record.get("stocks", [])
        print(f"Pool contains {len(pool_stocks)} stocks")

        # Check stocks with tech data
        stocks_with_tech = [s for s in pool_stocks if "tech" in s and s["tech"]]
        print(f"Stocks with tech data: {len(stocks_with_tech)}")

        if stocks_with_tech:
            print("\nSample stocks with tech data:")
            for i, stock in enumerate(stocks_with_tech[:5]):
                print(f"  {i+1}. {stock['code']}: {stock['tech']}")

            # Check specific stock if it has multiple strategies
            print("\nDetailed view of first stock with tech data:")
            first_stock = stocks_with_tech[0]
            print(f"  Code: {first_stock['code']}")
            print(f"  Score: {first_stock['score']}")
            print(f"  Value: {first_stock['value']}")
            print(f"  Tech data:")
            for strategy_name, tech_data in first_stock['tech'].items():
                print(f"    {strategy_name}:")
                print(f"      Score: {tech_data['score']}")
                print(f"      Value: {tech_data['value']}")
        else:
            print("ERROR: No stocks have tech data!")

        # Check stocks without tech data
        stocks_without_tech = [s for s in pool_stocks if "tech" not in s or not s["tech"]]
        print(f"\nStocks without tech data: {len(stocks_without_tech)}")

        if stocks_without_tech:
            print("Sample stocks without tech data:")
            for i, stock in enumerate(stocks_without_tech[:5]):
                print(f"  {i+1}. {stock['code']}")
                if "tech" in stock:
                    print(f"    Tech field exists but is empty: {stock['tech']}")
                else:
                    print(f"    No tech field")

        return True

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db_manager.close_connection()

def main():
    """Main function"""
    print("Checking pool tech data...")

    success = check_pool_data()

    if success:
        print("\n✓ Check completed successfully")
    else:
        print("\n✗ Check failed")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())

