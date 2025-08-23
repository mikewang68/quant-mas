#!/usr/bin/env python3
"""
Test script to check all records in the pool collection and verify strategy information.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mongodb_manager import MongoDBManager

def check_all_pool_records():
    """Check all records in the pool collection"""
    try:
        # Initialize MongoDB manager
        db_manager = MongoDBManager()

        # Get pool collection
        pool_collection = db_manager.pool_collection

        # Get all recent records (last 10)
        recent_records = list(pool_collection.find(
            {},
            {"_id": 0, "date": 1, "strategy_name": 1, "strategy_id": 1, "strategy_params": 1}
        ).sort("_id", -1).limit(10))

        print("=== Most Recent Pool Records ===")
        for i, record in enumerate(recent_records):
            print(f"\nRecord {i+1}:")
            print(f"  Date: {record.get('date', 'N/A')}")
            print(f"  Strategy Name: {record.get('strategy_name', 'N/A')}")
            print(f"  Strategy ID: {record.get('strategy_id', 'N/A')}")
            print(f"  Strategy Params: {record.get('strategy_params', 'N/A')}")

        # Check for records with specific strategy names
        three_ma_records = list(pool_collection.find(
            {"strategy_name": {"$regex": "三均线"}},
            {"_id": 0, "date": 1, "strategy_name": 1, "strategy_id": 1, "strategy_params": 1}
        ).sort("_id", -1).limit(5))

        trend_following_records = list(pool_collection.find(
            {"strategy_name": {"$regex": "趋势跟踪"}},
            {"_id": 0, "date": 1, "strategy_name": 1, "strategy_id": 1, "strategy_params": 1}
        ).sort("_id", -1).limit(5))

        print(f"\n=== Recent Three MA Strategy Records ===")
        print(f"Found {len(three_ma_records)} records")
        for i, record in enumerate(three_ma_records):
            print(f"\nRecord {i+1}:")
            print(f"  Date: {record.get('date', 'N/A')}")
            print(f"  Strategy Name: {record.get('strategy_name')}")
            print(f"  Strategy ID: {record.get('strategy_id')}")
            print(f"  Strategy Params: {record.get('strategy_params')}")

        print(f"\n=== Recent Trend Following Strategy Records ===")
        print(f"Found {len(trend_following_records)} records")
        for i, record in enumerate(trend_following_records):
            print(f"\nRecord {i+1}:")
            print(f"  Date: {record.get('date', 'N/A')}")
            print(f"  Strategy Name: {record.get('strategy_name')}")
            print(f"  Strategy ID: {record.get('strategy_id')}")
            print(f"  Strategy Params: {record.get('strategy_params')}")

        # Verify that the strategy information is correct
        correct_three_ma = 0
        correct_trend_following = 0

        for record in three_ma_records:
            if "三均线多头排列策略" in record.get('strategy_name', ''):
                correct_three_ma += 1

        for record in trend_following_records:
            if "趋势跟踪策略" in record.get('strategy_name', ''):
                correct_trend_following += 1

        print(f"\n=== Verification Results ===")
        print(f"Correct Three MA Strategy Records: {correct_three_ma}/{len(three_ma_records)}")
        print(f"Correct Trend Following Strategy Records: {correct_trend_following}/{len(trend_following_records)}")

        if correct_three_ma > 0:
            print("✓ Some Three MA Strategy records have correct strategy name")
        if correct_trend_following > 0:
            print("✓ Some Trend Following Strategy records have correct strategy name")

        return True

    except Exception as e:
        print(f"Error checking pool records: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        try:
            db_manager.close_connection()
        except:
            pass

if __name__ == "__main__":
    success = check_all_pool_records()
    if not success:
        sys.exit(1)

