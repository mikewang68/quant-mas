#!/usr/bin/env python3
"""
Test script to verify the signal data flow from strategy to database
"""

import sys
import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mongodb_manager import MongoDBManager
from strategies.signal_generation_v1_strategy import SignalGenerationV1Strategy


def test_signal_data_flow():
    """Test the complete signal data flow"""
    print("Testing signal data flow...")

    try:
        # Initialize database manager
        db_manager = MongoDBManager()

        # Initialize strategy
        strategy = SignalGenerationV1Strategy()

        # Execute strategy
        print("Executing signal generation strategy...")
        results = strategy.execute({}, "信号生成Agent", db_manager)

        print(f"Strategy execution completed. Generated {len(results)} results")

        # Check if results contain signals data
        if results:
            first_result = results[0]
            print(f"First result keys: {list(first_result.keys())}")

            if 'signals' in first_result:
                signals = first_result['signals']
                print(f"Signals data found: {signals}")
                print("✓ PASS: Strategy returns signals data")
            else:
                print("✗ FAIL: Strategy does not return signals data")
                return False

            # Check if signals contain expected fields
            expected_fields = ['counts', 'action', 'score_calc', 'signal_calc', 'score_ai', 'signal_ai', 'reason_ai']
            missing_fields = [field for field in expected_fields if field not in signals]
            if missing_fields:
                print(f"✗ FAIL: Missing fields in signals data: {missing_fields}")
                return False
            else:
                print("✓ PASS: All expected fields present in signals data")
        else:
            print("No results generated, skipping data validation")

        # Check database for latest pool record
        print("\nChecking database for latest pool record...")
        pool_collection = db_manager.db['pool']
        latest_record = pool_collection.find_one(sort=[("_id", -1)])

        if latest_record:
            stocks = latest_record.get('stocks', [])
            print(f"Found {len(stocks)} stocks in latest pool record")

            if stocks:
                # Check first stock for signals data
                first_stock = stocks[0]
                code = first_stock.get('code', 'Unknown')
                print(f"Checking stock {code} for signals data...")

                if 'signals' in first_stock:
                    signals = first_stock['signals']
                    print(f"Signals field found in database: {list(signals.keys())}")

                    # Check if "信号生成V1" strategy data exists
                    if '信号生成V1' in signals:
                        signal_data = signals['信号生成V1']
                        print(f"'信号生成V1' data found: {signal_data}")
                        print("✓ PASS: Database contains '信号生成V1' signals data")
                        return True
                    else:
                        print("✗ FAIL: '信号生成V1' data not found in signals")
                        print(f"Available strategies: {list(signals.keys())}")
                        return False
                else:
                    print("✗ FAIL: No signals field in stock data")
                    return False
            else:
                print("No stocks in pool record")
                return True
        else:
            print("No pool records found")
            return True

    except Exception as e:
        print(f"✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_signal_data_flow()
    if success:
        print("\nSignal data flow test completed successfully!")
    else:
        print("\nSignal data flow test failed!")
        sys.exit(1)

