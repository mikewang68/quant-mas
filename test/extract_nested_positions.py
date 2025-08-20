#!/usr/bin/env python3
"""
Extract and display nested position information from the latest pool record
"""

import sys
import os

# Add the project root directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from data.mongodb_manager import MongoDBManager
import json

def extract_nested_positions():
    """Extract nested position information from the latest pool record"""
    print("Extracting nested position information from the latest pool record...")

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
        print(f"  Total Stocks: {latest_record.get('count', 'N/A')}")

        # Get stocks
        stocks = latest_record.get('stocks', [])
        print(f"\nAnalyzing {len(stocks)} stocks for nested position information...")

        # Extract all nested position information
        stocks_with_nested_positions = []

        for i, stock in enumerate(stocks):
            # Look for nested position in tech_analysis.acc_up_trend
            tech_analysis = stock.get('tech_analysis', {})
            acc_up_trend = tech_analysis.get('acc_up_trend', {})
            position = acc_up_trend.get('position')

            if position is not None:
                stocks_with_nested_positions.append({
                    'index': i,
                    'code': stock.get('code', 'N/A'),
                    'position': position,
                    'full_nested_structure': {
                        'tech_analysis': {
                            'acc_up_trend': acc_up_trend
                        }
                    }
                })

        print(f"\nFound {len(stocks_with_nested_positions)} stocks with nested position information:")

        # Display detailed information for stocks with nested positions
        for i, stock_info in enumerate(stocks_with_nested_positions):
            print(f"\n{i+1}. Stock Code: {stock_info['code']}")
            print(f"   Position: {stock_info['position']}")
            print(f"   Full nested structure:")
            print(f"     tech_analysis:")
            print(f"       acc_up_trend:")
            acc_up_trend = stock_info['full_nested_structure']['tech_analysis']['acc_up_trend']
            for key, value in acc_up_trend.items():
                print(f"         {key}: {value}")

            # Stop after showing 20 stocks to avoid too much output
            if i >= 19 and len(stocks_with_nested_positions) > 20:
                print(f"\n   ... and {len(stocks_with_nested_positions) - 20} more stocks with nested positions")
                break

        # Summary statistics
        if stocks_with_nested_positions:
            positions = [s['position'] for s in stocks_with_nested_positions]
            print(f"\nPosition Statistics:")
            print(f"  Count: {len(positions)}")
            print(f"  Min: {min(positions)}")
            print(f"  Max: {max(positions)}")
            print(f"  Average: {sum(positions) / len(positions):.2f}")

        db_manager.close_connection()
        print("\n✓ Nested position extraction completed successfully")
        return True

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = extract_nested_positions()
    sys.exit(0 if success else 1)

