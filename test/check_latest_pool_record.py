#!/usr/bin/env python3
"""
Check the latest record in the pool collection with detailed information
"""

import sys
import os

# Add the project root directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from data.mongodb_manager import MongoDBManager
import json

def check_latest_pool_record():
    """Check the latest record in the pool collection"""
    print("Checking the latest record in pool collection...")

    try:
        # Initialize database manager
        db_manager = MongoDBManager()
        print("✓ Database connection established")

        # Get pool collection
        pool_collection = db_manager.db['pool']

        # Get the latest record sorted by selection date
        latest_record = pool_collection.find_one(sort=[('selection_date', -1)])

        if not latest_record:
            print("No records found in pool collection")
            return False

        print(f"\nLatest record in pool collection:")
        print(f"  ID: {latest_record.get('_id', 'N/A')}")
        print(f"  Agent Name: {latest_record.get('agent_name', 'N/A')}")
        print(f"  Strategy Name: {latest_record.get('strategy_name', 'N/A')}")
        print(f"  Selection Date: {latest_record.get('selection_date', 'N/A')}")
        print(f"  Selection Timestamp: {latest_record.get('selection_timestamp', 'N/A')}")
        print(f"  Count: {latest_record.get('count', 'N/A')}")
        print(f"  Created At: {latest_record.get('created_at', 'N/A')}")
        print(f"  Updated At: {latest_record.get('updated_at', 'N/A')}")

        # Show strategy parameters if available
        strategy_params = latest_record.get('strategy_parameters', {})
        if strategy_params:
            print(f"  Strategy Parameters:")
            for key, value in strategy_params.items():
                print(f"    {key}: {value}")

        # Show stocks information
        stocks = latest_record.get('stocks', [])
        print(f"  Number of Stocks: {len(stocks)}")

        if stocks:
            print(f"\n  First 5 stocks:")
            for i, stock in enumerate(stocks[:5]):
                print(f"    {i+1}. Code: {stock.get('code', 'N/A')}")
                print(f"       Selection Reason: {stock.get('selection_reason', 'N/A')}")
                print(f"       Score: {stock.get('score', 'N/A')}")

                # Show technical analysis if available
                tech_analysis = stock.get('tech_analysis', {})
                if tech_analysis:
                    print(f"       Technical Analysis:")
                    for key, value in tech_analysis.items():
                        print(f"         {key}: {value}")

                # Show position if available
                if 'position' in stock:
                    print(f"       Position: {stock.get('position', 'N/A')}")

                # Show all fields in the stock record
                print(f"       All Fields:")
                for key, value in stock.items():
                    if key not in ['code', 'selection_reason', 'score', 'tech_analysis', 'position']:
                        print(f"         {key}: {value}")

                print()

        db_manager.close_connection()
        print("✓ Latest pool record check completed successfully")
        return True

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = check_latest_pool_record()
    sys.exit(0 if success else 1)

