#!/usr/bin/env python3
"""
Test script to verify that the strategy results are correctly saved to the database
with the correct strategy information.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mongodb_manager import MongoDBManager
from datetime import datetime

def check_saved_strategy_results():
    """Check that strategy results are saved with correct strategy information"""
    try:
        # Initialize MongoDB manager
        db_manager = MongoDBManager()

        # Get pool collection
        pool_collection = db_manager.pool_collection

        # Get today's date
        today = datetime.now().strftime('%Y-%m-%d')

        # Find recent records in the pool
        recent_records = list(pool_collection.find(
            {"date": today},
            {"_id": 0, "strategy_name": 1, "strategy_id": 1, "strategy_params": 1}
        ).sort("_id", -1).limit(10))

        print("=== Recently Saved Strategy Results ===")
        for i, record in enumerate(recent_records):
            print(f"\nRecord {i+1}:")
            print(f"  Strategy Name: {record.get('strategy_name', 'N/A')}")
            print(f"  Strategy ID: {record.get('strategy_id', 'N/A')}")
            print(f"  Strategy Params: {record.get('strategy_params', 'N/A')}")

        # Check for specific strategies
        three_ma_records = list(pool_collection.find(
            {"date": today, "strategy_name": {"$regex": "三均线"}},
            {"_id": 0, "strategy_name": 1, "strategy_id": 1, "strategy_params": 1}
        ))

        trend_following_records = list(pool_collection.find(
            {"date": today, "strategy_name": {"$regex": "趋势跟踪"}},
            {"_id": 0, "strategy_name": 1, "strategy_id": 1, "strategy_params": 1}
        ))

        print(f"\n=== Three MA Strategy Records ===")
        print(f"Found {len(three_ma_records)} records")
        for record in three_ma_records[:3]:  # Show first 3
            print(f"  Strategy Name: {record.get('strategy_name')}")
            print(f"  Strategy ID: {record.get('strategy_id')}")
            print(f"  Strategy Params: {record.get('strategy_params')}")

        print(f"\n=== Trend Following Strategy Records ===")
        print(f"Found {len(trend_following_records)} records")
        for record in trend_following_records[:3]:  # Show first 3
            print(f"  Strategy Name: {record.get('strategy_name')}")
            print(f"  Strategy ID: {record.get('strategy_id')}")
            print(f"  Strategy Params: {record.get('strategy_params')}")

        # Verify that the strategy information is correct
        if three_ma_records:
            first_record = three_ma_records[0]
            if "三均线多头排列策略" in first_record.get('strategy_name', ''):
                print("\n✓ Three MA Strategy records have correct strategy name")
            else:
                print("\n✗ Three MA Strategy records have incorrect strategy name")

        if trend_following_records:
            first_record = trend_following_records[0]
            if "趋势跟踪策略" in first_record.get('strategy_name', ''):
                print("✓ Trend Following Strategy records have correct strategy name")
            else:
                print("✗ Trend Following Strategy records have incorrect strategy name")

        return True

    except Exception as e:
        print(f"Error checking saved results: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        try:
            db_manager.close_connection()
        except:
            pass

if __name__ == "__main__":
    success = check_saved_strategy_results()
    if not success:
        sys.exit(1)

