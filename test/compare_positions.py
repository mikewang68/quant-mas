#!/usr/bin/env python3
"""
Compare position calculation between different pool records
"""

import sys
import os

# Add the project root directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from data.mongodb_manager import MongoDBManager
import json
import numpy as np

def compare_position_calculations():
    """Compare position calculations between different pool records"""
    print("Comparing position calculations between different pool records...")

    try:
        # Initialize database manager
        db_manager = MongoDBManager()
        print("✓ Database connection established")

        # Get pool collection
        pool_collection = db_manager.db['pool']

        # Get multiple records to understand the pattern
        records = list(pool_collection.find().sort('selection_date', -1).limit(10))

        print(f"\nFound {len(records)} recent pool records:")

        for i, record in enumerate(records):
            print(f"\n--- Record {i+1} ---")
            print(f"  ID: {record.get('_id', 'N/A')}")
            print(f"  Strategy Name: {record.get('strategy_name', 'N/A')}")
            print(f"  Selection Date: {record.get('selection_date', 'N/A')}")
            print(f"  Total Stocks: {record.get('count', 'N/A')}")

            # Check stocks structure
            stocks = record.get('stocks', [])
            if stocks:
                # Check for different position structures
                stocks_with_top_level_position = [s for s in stocks if 'position' in s]
                stocks_with_nested_position = []

                for stock in stocks:
                    tech_analysis = stock.get('tech_analysis', {})
                    acc_up_trend = tech_analysis.get('acc_up_trend', {})
                    if 'position' in acc_up_trend:
                        stocks_with_nested_position.append({
                            'stock': stock,
                            'position': acc_up_trend['position']
                        })

                print(f"  Stocks with top-level position: {len(stocks_with_top_level_position)}")
                print(f"  Stocks with nested position: {len(stocks_with_nested_position)}")

                # Analyze the record with top-level positions (older record)
                if stocks_with_top_level_position and i == 1:  # Second record (2025-32)
                    print(f"\nAnalyzing top-level position record (older):")
                    positions = [s['position'] for s in stocks_with_top_level_position if s['position'] is not None]
                    if positions:
                        print(f"    Position range: {min(positions)} - {max(positions)}")
                        print(f"    Average position: {np.mean(positions):.2f}")
                        print(f"    Median position: {np.median(positions):.2f}")

                        # Check if positions are mostly 1.0 or -1.0 (as in the base strategy)
                        ones = [p for p in positions if abs(abs(p) - 1.0) < 0.1]
                        print(f"    Positions near 1.0 or -1.0: {len(ones)}/{len(positions)}")

                        # Show sample positions
                        print(f"    Sample positions: {positions[:10]}")

                # Analyze the record with nested positions (latest record)
                if stocks_with_nested_position and i == 0:  # First record (2025-33)
                    print(f"\nAnalyzing nested position record (latest):")
                    positions = [item['position'] for item in stocks_with_nested_position]
                    if positions:
                        print(f"    Position range: {min(positions)} - {max(positions)}")
                        print(f"    Average position: {np.mean(positions):.2f}")
                        print(f"    Median position: {np.median(positions):.2f}")

                        # Show sample positions
                        print(f"    Sample positions: {positions[:10]}")

        # Focus on the key records
        if len(records) >= 2:
            older_record = records[1]  # 2025-32
            latest_record = records[0]  # 2025-33

            print(f"\n--- Comparison ---")
            print(f"Older record ({older_record.get('_id')}):")
            print(f"  Strategy: {older_record.get('strategy_name', 'N/A')}")
            older_stocks = older_record.get('stocks', [])
            older_positions = [s['position'] for s in older_stocks if 'position' in s and s['position'] is not None]
            if older_positions:
                print(f"  Position range: {min(older_positions)} - {max(older_positions)}")
                ones = [p for p in older_positions if abs(abs(p) - 1.0) < 0.1]
                print(f"  Positions near 1.0 or -1.0: {len(ones)}/{len(older_positions)}")

            print(f"\nLatest record ({latest_record.get('_id')}):")
            print(f"  Strategy: {latest_record.get('strategy_name', 'N/A')}")
            latest_stocks = latest_record.get('stocks', [])
            latest_nested_positions = []
            for stock in latest_stocks:
                tech_analysis = stock.get('tech_analysis', {})
                acc_up_trend = tech_analysis.get('acc_up_trend', {})
                if 'position' in acc_up_trend:
                    latest_nested_positions.append(acc_up_trend['position'])

            if latest_nested_positions:
                print(f"  Position range: {min(latest_nested_positions)} - {max(latest_nested_positions)}")
                print(f"  Average position: {np.mean(latest_nested_positions):.2f}")

        db_manager.close_connection()
        print("\n✓ Position calculation comparison completed successfully")
        return True

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = compare_position_calculations()
    sys.exit(0 if success else 1)

