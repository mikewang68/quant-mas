#!/usr/bin/env python3
"""
Check records in the pool collection that contain position information
"""

import sys
import os

# Add the project root directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from data.mongodb_manager import MongoDBManager
import json

def check_pool_records_with_position():
    """Check records in the pool collection that contain position information"""
    print("Checking records in pool collection with position information...")

    try:
        # Initialize database manager
        db_manager = MongoDBManager()
        print("✓ Database connection established")

        # Get pool collection
        pool_collection = db_manager.db['pool']

        # Get all records sorted by selection date (newest first)
        records = list(pool_collection.find().sort('selection_date', -1))

        print(f"Found {len(records)} total records in pool")

        # Look for records with position information
        records_with_position = []
        for record in records:
            stocks = record.get('stocks', [])
            # Check if any stock has position field
            for stock in stocks:
                if 'position' in stock:
                    records_with_position.append(record)
                    break

        print(f"Found {len(records_with_position)} records with position information")

        if records_with_position:
            # Show the latest record with position information
            latest_record = records_with_position[0]
            print(f"\nLatest record with position information:")
            print(f"  ID: {latest_record.get('_id', 'N/A')}")
            print(f"  Agent Name: {latest_record.get('agent_name', 'N/A')}")
            print(f"  Strategy Name: {latest_record.get('strategy_name', 'N/A')}")
            print(f"  Selection Date: {latest_record.get('selection_date', 'N/A')}")
            print(f"  Count: {latest_record.get('count', 'N/A')}")

            # Show stocks with position information
            stocks = latest_record.get('stocks', [])
            stocks_with_position = [s for s in stocks if 'position' in s]
            print(f"  Stocks with position: {len(stocks_with_position)}")

            if stocks_with_position:
                print(f"\n  First 10 stocks with position:")
                for i, stock in enumerate(stocks_with_position[:10]):
                    print(f"    {i+1}. Code: {stock.get('code', 'N/A')}")
                    print(f"       Position: {stock.get('position', 'N/A')}")
                    print(f"       Selection Reason: {stock.get('selection_reason', 'N/A')}")
                    print(f"       Score: {stock.get('score', 'N/A')}")

                    # Show technical analysis if available
                    tech_analysis = stock.get('tech_analysis', {})
                    if tech_analysis:
                        print(f"       Technical Analysis:")
                        for key, value in tech_analysis.items():
                            if key == 'acc_up_trend' and isinstance(value, dict):
                                print(f"         Accelerating Uptrend:")
                                for k, v in value.items():
                                    print(f"           {k}: {v}")
                            else:
                                print(f"         {key}: {value}")

                    print()

        else:
            print("No records with position information found")

            # Show the latest record for reference
            if records:
                latest_record = records[0]
                print(f"\nLatest record (for reference):")
                print(f"  ID: {latest_record.get('_id', 'N/A')}")
                print(f"  Agent Name: {latest_record.get('agent_name', 'N/A')}")
                print(f"  Strategy Name: {latest_record.get('strategy_name', 'N/A')}")
                print(f"  Selection Date: {latest_record.get('selection_date', 'N/A')}")
                print(f"  Count: {latest_record.get('count', 'N/A')}")

        db_manager.close_connection()
        print("✓ Pool records check completed successfully")
        return True

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = check_pool_records_with_position()
    sys.exit(0 if success else 1)

